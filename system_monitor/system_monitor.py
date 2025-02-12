import psutil
import platform
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.progress import ProgressBar, BarColumn, Progress
from datetime import datetime
import time
from rich.align import Align
import speedtest
import threading
import queue
import socket
import psutil._common
from datetime import timedelta
from pynput import keyboard
import signal
from rich.prompt import Prompt
import sys
import select

console = Console()

# Custom color schemes
COLORS = {
    "title": "bold cyan",
    "header": "bold blue",
    "normal": "green",
    "warning": "yellow",
    "critical": "red",
    "border": "bright_blue"
}

# Add these global variables after COLORS
SPEED_TEST_INTERVAL = 300  # Speed test every 5 minutes
speed_queue = queue.Queue()
speed_history = {'download': [], 'upload': []}
MAX_HISTORY_POINTS = 10
command_queue = queue.Queue()
ANALYTICS_STATE = {
    "show_speed_test": True,
    "show_process_list": False,
    "show_network_details": True,
    "show_disk_io": False,
    "show_temperature": False,  # If supported by system
}

# Add these global variables
running = True
keyboard_listener = None

def get_colored_percentage(percentage):
    """Return colored percentage based on value"""
    if percentage < 60:
        return f"[green]{percentage}%[/green]"
    elif percentage < 80:
        return f"[yellow]{percentage}%[/yellow]"
    return f"[red]{percentage}%[/red]"

def get_size(bytes):
    """
    Convert bytes to human readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}"
        bytes /= 1024

def create_progress_bar(percentage):
    """Create a stylized progress bar"""
    progress = ProgressBar(total=100, completed=percentage)
    return progress

def get_system_info():
    """Get detailed system information"""
    system_table = Table(
        border_style=COLORS["border"],
        header_style=COLORS["header"],
        pad_edge=False,
        box=None
    )
    
    system_table.add_column("Component", style="cyan")
    system_table.add_column("Details", style="bright_white")
    
    # System information
    system_table.add_row("OS", f"{platform.system()} {platform.release()}")
    system_table.add_row("Version", platform.version())
    system_table.add_row("Machine", platform.machine())
    system_table.add_row("Processor", platform.processor())
    system_table.add_row("Hostname", socket.gethostname())
    system_table.add_row("Boot Time", datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'))
    uptime = str(timedelta(seconds=int(time.time() - psutil.boot_time())))
    system_table.add_row("Uptime", uptime)
    
    return Panel(
        system_table,
        title="[bold cyan]System Information[/bold cyan]",
        border_style=COLORS["border"],
        padding=(1, 2)
    )

def get_cpu_info():
    """Enhanced CPU information"""
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    cpu_freq = psutil.cpu_freq(percpu=False)
    cpu_stats = psutil.cpu_stats()
    cpu_count = psutil.cpu_count()
    cpu_count_logical = psutil.cpu_count(logical=False)
    
    cpu_table = Table(
        border_style=COLORS["border"],
        header_style=COLORS["header"],
        pad_edge=False,
        box=None
    )
    
    cpu_table.add_column("Metric", style="cyan")
    cpu_table.add_column("Value", justify="right")
    cpu_table.add_column("Details", justify="left", width=30)
    
    # Overall CPU usage
    total_cpu_usage = sum(cpu_percent) / len(cpu_percent)
    cpu_table.add_row(
        "Total CPU",
        get_colored_percentage(total_cpu_usage),
        Text(str(create_progress_bar(total_cpu_usage)))
    )
    
    # Individual core usage
    for i, percentage in enumerate(cpu_percent):
        cpu_table.add_row(
            f"Core {i}",
            get_colored_percentage(percentage),
            Text(str(create_progress_bar(percentage)))
        )
    
    # CPU frequency
    if cpu_freq:
        cpu_table.add_row(
            "Current Frequency",
            f"[bright_green]{cpu_freq.current:.2f}MHz[/bright_green]",
            f"(Min: {cpu_freq.min:.2f}MHz, Max: {cpu_freq.max:.2f}MHz)"
        )
    
    # CPU statistics
    cpu_table.add_row("Physical Cores", str(cpu_count_logical), "")
    cpu_table.add_row("Total Cores", str(cpu_count), "")
    cpu_table.add_row("Context Switches", f"{cpu_stats.ctx_switches:,}", "")
    cpu_table.add_row("Interrupts", f"{cpu_stats.interrupts:,}", "")
    
    return Panel(
        cpu_table,
        title="[bold cyan]CPU Statistics[/bold cyan]",
        border_style=COLORS["border"],
        padding=(1, 2)
    )

def get_memory_info():
    """Enhanced memory information"""
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    memory_table = Table(
        border_style=COLORS["border"],
        header_style=COLORS["header"],
        pad_edge=False,
        box=None
    )
    
    memory_table.add_column("Type", style="cyan")
    memory_table.add_column("Total", justify="right")
    memory_table.add_column("Used", justify="right")
    memory_table.add_column("Free", justify="right")
    memory_table.add_column("Available", justify="right")
    memory_table.add_column("Usage", justify="right")
    memory_table.add_column("Progress", justify="left", width=30)
    
    # RAM details
    memory_table.add_row(
        "RAM",
        get_size(memory.total),
        get_size(memory.used),
        get_size(memory.free),
        get_size(memory.available),
        get_colored_percentage(memory.percent),
        Text(str(create_progress_bar(memory.percent)))
    )
    
    # Swap details
    memory_table.add_row(
        "Swap",
        get_size(swap.total),
        get_size(swap.used),
        get_size(swap.free),
        "",  # Available column empty for swap
        get_colored_percentage(swap.percent),
        Text(str(create_progress_bar(swap.percent)))
    )
    
    # Add platform-specific memory details
    if platform.system() == "Linux":
        if hasattr(memory, 'buffers'):
            memory_table.add_row("Buffers", get_size(memory.buffers), "", "", "", "", "")
        if hasattr(memory, 'cached'):
            memory_table.add_row("Cached", get_size(memory.cached), "", "", "", "", "")
        if hasattr(memory, 'shared'):
            memory_table.add_row("Shared", get_size(memory.shared), "", "", "", "", "")
    elif platform.system() == "Darwin":  # macOS
        # Add macOS-specific memory stats if needed
        vm_stats = psutil.virtual_memory()
        memory_table.add_row(
            "Inactive",
            "",
            get_size(vm_stats.inactive) if hasattr(vm_stats, 'inactive') else "N/A",
            "", "", "", ""
        )
        memory_table.add_row(
            "Active",
            "",
            get_size(vm_stats.active) if hasattr(vm_stats, 'active') else "N/A",
            "", "", "", ""
        )
    
    return Panel(
        memory_table,
        title="[bold cyan]Memory Statistics[/bold cyan]",
        border_style=COLORS["border"],
        padding=(1, 2)
    )

def get_disk_info():
    """
    Get disk usage information with enhanced visuals
    """
    disk_table = Table(
        border_style=COLORS["border"],
        header_style=COLORS["header"],
        pad_edge=False,
        box=None
    )
    
    disk_table.add_column("Device", style="cyan")
    disk_table.add_column("Mount", style="bright_blue")
    disk_table.add_column("Total", justify="right")
    disk_table.add_column("Used", justify="right")
    disk_table.add_column("Free", justify="right")
    disk_table.add_column("Usage", justify="right")
    disk_table.add_column("Progress", justify="left", width=30)
    
    for partition in psutil.disk_partitions():
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            progress = create_progress_bar(partition_usage.percent)
            disk_table.add_row(
                partition.device,
                partition.mountpoint,
                get_size(partition_usage.total),
                get_size(partition_usage.used),
                get_size(partition_usage.free),
                get_colored_percentage(partition_usage.percent),
                Text(str(progress))
            )
        except PermissionError:
            continue
    
    return Panel(
        disk_table,
        title="[bold cyan]Disk Statistics[/bold cyan]",
        border_style=COLORS["border"],
        padding=(1, 2)
    )

def speed_test_worker():
    """Background worker for speed testing"""
    while True:
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            
            speed_history['download'].append(download_speed)
            speed_history['upload'].append(upload_speed)
            
            # Keep only last N points
            speed_history['download'] = speed_history['download'][-MAX_HISTORY_POINTS:]
            speed_history['upload'] = speed_history['upload'][-MAX_HISTORY_POINTS:]
            
            speed_queue.put({
                'download': download_speed,
                'upload': upload_speed,
                'timestamp': datetime.now()
            })
        except:
            speed_queue.put(None)
        
        time.sleep(SPEED_TEST_INTERVAL)

def get_network_info():
    """Enhanced network information"""
    network_table = Table(
        border_style=COLORS["border"],
        header_style=COLORS["header"],
        pad_edge=False,
        box=None
    )
    
    network_table.add_column("Interface", style="cyan")
    network_table.add_column("Sent", justify="right")
    network_table.add_column("Received", justify="right")
    network_table.add_column("Status", justify="center")
    network_table.add_column("Address", justify="right")
    network_table.add_column("Transfer Rate", justify="right")
    
    # Store previous counters for calculating rates
    if not hasattr(get_network_info, 'prev_counters'):
        get_network_info.prev_counters = {}
        get_network_info.prev_time = time.time()
    
    current_time = time.time()
    time_delta = current_time - get_network_info.prev_time
    
    # Network interfaces
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                stats = psutil.net_if_stats().get(interface)
                if stats:
                    speed = f"{stats.speed}Mb/s" if stats.speed > 0 else "N/A"
                    status = "[green]●[/green] Up" if stats.isup else "[red]○[/red] Down"
                    
                    net_io = psutil.net_io_counters(pernic=True).get(interface)
                    if net_io:
                        # Calculate transfer rates
                        if interface in get_network_info.prev_counters:
                            prev_net_io = get_network_info.prev_counters[interface]
                            send_rate = (net_io.bytes_sent - prev_net_io.bytes_sent) / time_delta
                            recv_rate = (net_io.bytes_recv - prev_net_io.bytes_recv) / time_delta
                            rate_str = f"↑{get_size(send_rate)}/s ↓{get_size(recv_rate)}/s"
                        else:
                            rate_str = "Calculating..."
                        
                        get_network_info.prev_counters[interface] = net_io
                        
                        network_table.add_row(
                            interface,
                            f"[bright_green]{get_size(net_io.bytes_sent)}[/bright_green]",
                            f"[bright_blue]{get_size(net_io.bytes_recv)}[/bright_blue]",
                            status,
                            f"{addr.address} ({speed})",
                            rate_str
                        )
    
    get_network_info.prev_time = current_time
    
    # Speed test results
    try:
        speed_data = speed_queue.get_nowait()
        if speed_data:
            network_table.add_row(
                "[bold cyan]Speed Test[/bold cyan]",
                f"[bright_green]↑ {speed_data['upload']:.1f} Mbps[/bright_green]",
                f"[bright_blue]↓ {speed_data['download']:.1f} Mbps[/bright_blue]",
                f"[yellow]{speed_data['timestamp'].strftime('%H:%M:%S')}[/yellow]",
                "Last Test",
                ""
            )
            
            # Add visual representation of speed history using progress bars
            if speed_history['download']:
                max_speed = max(max(speed_history['download']), max(speed_history['upload']))
                down_progress = Progress(BarColumn(bar_width=20))
                up_progress = Progress(BarColumn(bar_width=20))
                
                current_down = speed_history['download'][-1]
                current_up = speed_history['upload'][-1]
                
                network_table.add_row(
                    "Download History",
                    "",
                    str(down_progress.add_task("", total=max_speed, completed=current_down)),
                    f"{current_down:.1f} Mbps",
                    "",
                    ""
                )
                network_table.add_row(
                    "Upload History",
                    "",
                    str(up_progress.add_task("", total=max_speed, completed=current_up)),
                    f"{current_up:.1f} Mbps",
                    "",
                    ""
                )
    except queue.Empty:
        pass
    
    return Panel(
        network_table,
        title="[bold cyan]Network Statistics[/bold cyan]",
        border_style=COLORS["border"],
        padding=(1, 2)
    )

def create_header():
    """Create a beautiful header with command help"""
    header = Table.grid(padding=1)
    header.add_column(style="cyan", justify="center")
    header.add_row(
        f"[bold cyan]System Monitor - {platform.system()} {platform.release()}[/bold cyan]"
    )
    header.add_row(
        "[yellow]Commands: (q)uit (h)elp (p)rocesses (d)isk I/O (s)peed test (n)etwork (t)emp | "
        f"Updated: {datetime.now().strftime('%H:%M:%S')}[/yellow]"
    )
    return Panel(header, style=COLORS["border"])

def input_listener(layout):
    """Listen for keyboard input"""
    global running
    while running:
        try:
            # Non-blocking input check
            if select.select([sys.stdin], [], [], 0.1)[0]:
                command = sys.stdin.read(1).lower()
                if command == 'q':
                    running = False
                    command_queue.put('quit')
                elif command == 's':
                    ANALYTICS_STATE['show_speed_test'] = not ANALYTICS_STATE['show_speed_test']
                    console.print("[yellow]Speed Test:", "On" if ANALYTICS_STATE['show_speed_test'] else "Off")
                elif command == 'p':
                    ANALYTICS_STATE['show_process_list'] = not ANALYTICS_STATE['show_process_list']
                    console.print("[yellow]Process List:", "On" if ANALYTICS_STATE['show_process_list'] else "Off")
                elif command == 'n':
                    ANALYTICS_STATE['show_network_details'] = not ANALYTICS_STATE['show_network_details']
                    console.print("[yellow]Network Details:", "On" if ANALYTICS_STATE['show_network_details'] else "Off")
                elif command == 'd':
                    ANALYTICS_STATE['show_disk_io'] = not ANALYTICS_STATE['show_disk_io']
                    console.print("[yellow]Disk I/O:", "On" if ANALYTICS_STATE['show_disk_io'] else "Off")
                elif command == 't':
                    ANALYTICS_STATE['show_temperature'] = not ANALYTICS_STATE['show_temperature']
                    console.print("[yellow]Temperature:", "On" if ANALYTICS_STATE['show_temperature'] else "Off")
                elif command == 'h':
                    show_help()
                command_queue.put('refresh')
                # Immediately update the layout after a command
                update_layout(layout)
        except (IOError, KeyboardInterrupt):
            pass

def get_process_info():
    """Get information about running processes"""
    process_table = Table(
        border_style=COLORS["border"],
        header_style=COLORS["header"],
        pad_edge=False,
        box=None
    )
    
    process_table.add_column("PID", style="cyan", justify="right")
    process_table.add_column("Name", style="bright_blue")
    process_table.add_column("CPU %", justify="right")
    process_table.add_column("Memory %", justify="right")
    process_table.add_column("Status", justify="center")
    
    try:
        processes = sorted(
            [proc.info for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status'])],
            key=lambda x: x['cpu_percent'] or 0,
            reverse=True
        )[:10]  # Show top 10 processes
        
        for proc in processes:
            try:
                process_table.add_row(
                    str(proc['pid']),
                    proc['name'][:20],
                    f"{proc['cpu_percent']:.1f}%",
                    f"{proc['memory_percent']:.1f}%",
                    proc['status']
                )
            except (KeyError, psutil.NoSuchProcess):
                continue
    except Exception as e:
        process_table.add_row("Error", str(e), "", "", "")
    
    return Panel(
        process_table,
        title="[bold cyan]Top Processes[/bold cyan]",
        border_style=COLORS["border"],
        padding=(1, 2)
    )

def get_disk_io_info():
    """Get disk I/O statistics"""
    if not ANALYTICS_STATE['show_disk_io']:
        return None
        
    disk_io_table = Table(
        border_style=COLORS["border"],
        header_style=COLORS["header"],
        pad_edge=False,
        box=None
    )
    
    disk_io_table.add_column("Disk", style="cyan")
    disk_io_table.add_column("Read", justify="right")
    disk_io_table.add_column("Write", justify="right")
    disk_io_table.add_column("Read Speed", justify="right")
    disk_io_table.add_column("Write Speed", justify="right")
    
    disk_io = psutil.disk_io_counters(perdisk=True)
    for disk_name, counters in disk_io.items():
        disk_io_table.add_row(
            disk_name,
            get_size(counters.read_bytes),
            get_size(counters.write_bytes),
            f"{get_size(counters.read_bytes / counters.read_time if counters.read_time > 0 else 0)}/s",
            f"{get_size(counters.write_bytes / counters.write_time if counters.write_time > 0 else 0)}/s"
        )
    
    return Panel(
        disk_io_table,
        title="[bold cyan]Disk I/O Statistics[/bold cyan]",
        border_style=COLORS["border"],
        padding=(1, 2)
    )

def get_temperature_info():
    """Get temperature information"""
    if not ANALYTICS_STATE['show_temperature']:
        return None

    temperature_table = Table(
        border_style=COLORS["border"],
        header_style=COLORS["header"],
        pad_edge=False,
        box=None
    )

    temperature_table.add_column("Sensor", style="cyan")
    temperature_table.add_column("Temperature", justify="right")

    try:
        # Check if the sensors_temperatures function is available
        if hasattr(psutil, 'sensors_temperatures'):
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        temperature_table.add_row(
                            entry.label or name,
                            f"{entry.current}°C"
                        )
            else:
                temperature_table.add_row("No sensors found", "")
        else:
            temperature_table.add_row("Not supported on this platform", "")
    except Exception as e:
        temperature_table.add_row("Error", str(e))

    return Panel(
        temperature_table,
        title="[bold cyan]Temperature Statistics[/bold cyan]",
        border_style=COLORS["border"],
        padding=(1, 2)
    )

def signal_handler(signum, frame):
    """Handle system signals"""
    global running
    running = False
    command_queue.put('quit')

def update_layout(layout):
    """Update layout based on current state"""
    try:
        # Update visibility of optional panels
        layout["processes"].visible = ANALYTICS_STATE['show_process_list']
        layout["disk_io"].visible = ANALYTICS_STATE['show_disk_io']
        layout["temperature"].visible = ANALYTICS_STATE['show_temperature']
    except Exception as e:
        console.print(f"[red]Layout update error: {e}[/red]")

def main():
    global running
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create the base layout
    layout = Layout()
    
    # Create the main split
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main")
    )
    
    # Create the main content area with initial layout
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    
    # Initialize the left and right layouts with fixed sections
    layout["left"].split_column(
        Layout(name="system", size=10),
        Layout(name="cpu", size=15),
        Layout(name="processes", size=15, visible=False)
    )
    
    layout["right"].split_column(
        Layout(name="memory", size=10),
        Layout(name="network", size=15),
        Layout(name="disk_io", size=15, visible=False),
        Layout(name="temperature", size=10, visible=False)
    )
    
    # Start input listener thread
    input_thread = threading.Thread(target=input_listener, args=(layout,), daemon=True)
    input_thread.start()
    
    # Start speed test worker thread
    speed_thread = threading.Thread(target=speed_test_worker, daemon=True)
    speed_thread.start()
    
    # Show initial help
    show_help()
    
    try:
        with Live(layout, refresh_per_second=2, screen=True):
            while running:
                try:
                    # Check for commands
                    try:
                        cmd = command_queue.get_nowait()
                        if cmd == 'quit':
                            break
                        elif cmd == 'refresh':
                            update_layout(layout)
                    except queue.Empty:
                        pass
                    
                    # Update all panels
                    layout["header"].update(create_header())
                    layout["system"].update(get_system_info())
                    layout["cpu"].update(get_cpu_info())
                    layout["memory"].update(get_memory_info())
                    layout["network"].update(get_network_info())
                    
                    # Update optional panels if visible
                    if ANALYTICS_STATE['show_process_list']:
                        layout["processes"].update(get_process_info())
                    
                    if ANALYTICS_STATE['show_disk_io']:
                        layout["disk_io"].update(get_disk_io_info())
                    
                    if ANALYTICS_STATE['show_temperature']:
                        layout["temperature"].update(get_temperature_info())
                    
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    break
    finally:
        running = False

def show_help():
    """Display help information"""
    help_text = """
[bold cyan]Available Commands:[/bold cyan]
Just press the key (no Enter needed):
[yellow]q[/yellow] - Quit the application
[yellow]s[/yellow] - Toggle Speed Test display
[yellow]p[/yellow] - Toggle Process List
[yellow]n[/yellow] - Toggle Network Details
[yellow]d[/yellow] - Toggle Disk I/O Statistics
[yellow]t[/yellow] - Toggle Temperature Monitor
[yellow]h[/yellow] - Show this help message
    """
    console.print(help_text)
    console.print("[yellow]Press any key to continue...[/yellow]")
    # Wait for a key press to continue
    input()

if __name__ == "__main__":
    console.clear()
    main() 