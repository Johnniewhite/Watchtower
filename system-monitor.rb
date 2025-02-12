class SystemMonitor < Formula
  include Language::Python::Virtualenv

  desc "Comprehensive system monitoring tool with real-time insights"
  homepage "https://github.com/johnniewhite/watchtower"
  url "https://files.pythonhosted.org/packages/source/w/watchtower/watchtower-0.1.0.tar.gz"
  sha256 "5478fc1bb904d05e45a3b31990cc1a3ece35e9e290432c4ed830dc92220a6ced"
  license "MIT"

  depends_on "python@3.9"

  resource "rich" do
    url "https://files.pythonhosted.org/packages/source/r/rich/rich-13.0.0.tar.gz"
    sha256 "5478fc1bb904d05e45a3b31990cc1a3ece35e9e290432c4ed830dc92220a6ced"
  end

  resource "psutil" do
    url "https://files.pythonhosted.org/packages/source/p/psutil/psutil-5.9.0.tar.gz"
    sha256 "5478fc1bb904d05e45a3b31990cc1a3ece35e9e290432c4ed830dc92220a6ced"
  end

  resource "speedtest-cli" do
    url "https://files.pythonhosted.org/packages/source/s/speedtest-cli/speedtest-cli-2.1.3.tar.gz"
    sha256 "5478fc1bb904d05e45a3b31990cc1a3ece35e9e290432c4ed830dc92220a6ced"
  end

  resource "pynput" do
    url "https://files.pythonhosted.org/packages/source/p/pynput/pynput-1.7.0.tar.gz"
    sha256 "5478fc1bb904d05e45a3b31990cc1a3ece35e9e290432c4ed830dc92220a6ced"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/system-monitor", "--version"
  end
end 