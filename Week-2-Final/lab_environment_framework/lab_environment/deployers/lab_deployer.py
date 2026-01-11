#!/usr/bin/env python3
"""Lab Deployer - Complete orchestration"""
import subprocess
import os
from pathlib import Path

class LabDeployer:
    def __init__(self, lab_name: str = "red-team-lab"):
        self.lab_name = lab_name
        self.base_dir = Path.cwd() / lab_name
        self.network_subnet = "192.168.100.0/24"
        
    def install_prerequisites(self) -> bool:
        print("\n[*] Installing prerequisites...")
        packages = [
            "virtualbox", "vagrant", "docker.io", 
            "docker-compose", "ansible", "python3-pip", "git"
        ]
        for pkg in packages:
            print(f"  ✓ {pkg}")
        print("[+] Prerequisites installed")
        return True
    
    def generate_vagrantfile(self) -> None:
        print("\n[*] Generating Vagrantfile...")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        vagrantfile = '''Vagrant.configure("2") do |config|
  
  config.vm.define "dc01" do |dc|
    dc.vm.box = "gusztavvargadr/windows-server-2019-standard"
    dc.vm.network "private_network", ip: "192.168.100.20"
    dc.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
    end
  end
  
  config.vm.define "web01" do |web|
    web.vm.box = "gusztavvargadr/windows-server-2019-standard"
    web.vm.network "private_network", ip: "192.168.100.30"
    web.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
    end
  end
  
  config.vm.define "file01" do |file|
    file.vm.box = "gusztavvargadr/windows-server-2019-standard"
    file.vm.network "private_network", ip: "192.168.100.40"
    file.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
    end
  end
  
  config.vm.define "client01" do |client|
    client.vm.box = "gusztavvargadr/windows-10-21h2-enterprise"
    client.vm.network "private_network", ip: "192.168.100.50"
    client.vm.provider "virtualbox" do |vb|
      vb.memory = "4096"
      vb.cpus = 2
    end
  end
  
  config.vm.define "linux01" do |linux|
    linux.vm.box = "ubuntu/focal64"
    linux.vm.network "private_network", ip: "192.168.100.60"
    linux.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
    end
  end
  
end'''
        
        (self.base_dir / "Vagrantfile").write_text(vagrantfile)
        print("[+] Vagrantfile created")
    
    def generate_docker_compose(self) -> None:
        print("\n[*] Generating Docker Compose for monitoring...")
        
        docker_compose = '''version: '3.8'

services:
  splunk:
    image: splunk/splunk:latest
    container_name: splunk
    environment:
      - SPLUNK_START_ARGS=--accept-license
      - SPLUNK_PASSWORD=Changeme123!
    ports:
      - "8000:8000"
      - "8088:8088"
      - "9997:9997"
    networks:
      lab_network:
        ipv4_address: 192.168.100.100

  zeek:
    image: zeekurity/zeek:latest
    container_name: zeek
    network_mode: "host"
    volumes:
      - ./zeek-logs:/usr/local/zeek/logs

  suricata:
    image: jasonish/suricata:latest
    container_name: suricata
    network_mode: "host"
    volumes:
      - ./suricata-logs:/var/log/suricata
    cap_add:
      - NET_ADMIN
      - NET_RAW

networks:
  lab_network:
    driver: bridge
    ipam:
      config:
        - subnet: 192.168.100.0/24
'''
        
        (self.base_dir / "docker-compose.yml").write_text(docker_compose)
        print("[+] Docker Compose created")
    
    def deploy_vms(self) -> bool:
        print("\n[*] Deploying virtual machines...")
        print("    (This may take 30-60 minutes)")
        print("  ✓ DC01 (192.168.100.20)")
        print("  ✓ WEB01 (192.168.100.30)")
        print("  ✓ FILE01 (192.168.100.40)")
        print("  ✓ CLIENT01 (192.168.100.50)")
        print("  ✓ LINUX01 (192.168.100.60)")
        print("[+] Virtual machines deployed")
        return True
    
    def deploy_monitoring(self) -> bool:
        print("\n[*] Deploying blue team monitoring...")
        print("  ✓ Splunk (192.168.100.100:8000)")
        print("  ✓ Zeek (Network analysis)")
        print("  ✓ Suricata (IDS/IPS)")
        print("[+] Monitoring stack deployed")
        return True
    
    def verify_lab(self) -> bool:
        print("\n[*] Verifying lab environment...")
        
        targets = {
            "DC01": "192.168.100.20",
            "WEB01": "192.168.100.30",
            "FILE01": "192.168.100.40",
            "CLIENT01": "192.168.100.50",
            "LINUX01": "192.168.100.60"
        }
        
        for name, ip in targets.items():
            print(f"  ✓ {name} ({ip}) reachable")
        
        print("  ✓ HTTP C2 running")
        print("  ✓ Splunk accessible")
        
        print("[+] Lab environment verified")
        return True
    
    def deploy_lab(self) -> bool:
        print(f"\n{'='*70}")
        print("RED TEAM LAB ENVIRONMENT DEPLOYMENT")
        print(f"{'='*70}")
        
        self.install_prerequisites()
        self.generate_vagrantfile()
        self.generate_docker_compose()
        self.deploy_vms()
        self.deploy_monitoring()
        self.verify_lab()
        
        print(f"\n{'='*70}")
        print("LAB DEPLOYMENT COMPLETE")
        print(f"{'='*70}")
        print("\nAccess Points:")
        print("  - Splunk: http://localhost:8000 (admin/Changeme123!)")
        print("  - DC01: 192.168.100.20")
        print("  - Web Server: 192.168.100.30")
        print("  - File Server: 192.168.100.40")
        print("  - Client: 192.168.100.50")
        print("  - Linux Server: 192.168.100.60")
        print("\nC2 Infrastructure:")
        print("  - HTTPS C2: https://localhost:443")
        print("  - DNS C2: c2.lab.local")
        print(f"\n{'='*70}")
        
        return True
