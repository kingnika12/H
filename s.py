#!/usr/bin/env python3
"""
Enhanced Website Load Testing Script
Optimized for Termux with advanced features for comprehensive testing.
For testing your own website's performance and load handling capabilities.
"""

import requests
import cloudscraper
import threading
import time
import statistics
import random
import socket
from datetime import datetime
from urllib.parse import urlparse
import json

class AdvancedWebsiteLoadTester:
    def __init__(self, url, num_threads=50, requests_per_thread=100, delay_between_requests=0.01, 
                 use_cloudscraper=True, flood_mode=False):
        self.url = url
        self.num_threads = num_threads
        self.requests_per_thread = requests_per_thread
        self.delay_between_requests = delay_between_requests
        self.use_cloudscraper = use_cloudscraper
        self.flood_mode = flood_mode
        self.results = []
        self.lock = threading.Lock()
        
        # Enhanced User Agents - 20 realistic ones
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vivaldi/6.5.3206.39',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
        
        # X-Forwarded and other headers for realistic requests
        self.proxy_ips = [
            '203.0.113.1', '198.51.100.1', '192.0.2.1', '203.0.113.195',
            '198.51.100.178', '192.0.2.146', '203.0.113.73', '198.51.100.92',
            '8.8.8.8', '1.1.1.1', '208.67.222.222', '9.9.9.9'
        ]
        
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL provided")
    
    def get_random_headers(self):
        """Generate realistic headers with random values"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9',
                'es-ES,es;q=0.9',
                'fr-FR,fr;q=0.9',
                'de-DE,de;q=0.9',
                'pt-BR,pt;q=0.9',
                'ru-RU,ru;q=0.9',
                'ja-JP,ja;q=0.9'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'X-Forwarded-For': random.choice(self.proxy_ips),
            'X-Real-IP': random.choice(self.proxy_ips),
            'X-Forwarded-Proto': 'https',
            'CF-Connecting-IP': random.choice(self.proxy_ips),
            'X-Originating-IP': random.choice(self.proxy_ips),
            'X-Remote-IP': random.choice(self.proxy_ips),
            'X-Client-IP': random.choice(self.proxy_ips),
            'True-Client-IP': random.choice(self.proxy_ips)
        }
        
        # Add some random additional headers occasionally
        if random.random() < 0.3:
            headers['Referer'] = random.choice([
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/',
                'https://www.facebook.com/',
                'https://twitter.com/',
                'https://www.reddit.com/'
            ])
        
        if random.random() < 0.2:
            headers['X-Requested-With'] = 'XMLHttpRequest'
        
        return headers
    
    def make_request(self):
        """Make a single HTTP request with enhanced features"""
        try:
            start_time = time.time()
            headers = self.get_random_headers()
            
            if self.use_cloudscraper:
                scraper = cloudscraper.create_scraper()
                response = scraper.get(
                    self.url,
                    headers=headers,
                    timeout=15,
                    allow_redirects=True
                )
            else:
                # Use requests with session for connection pooling
                session = requests.Session()
                response = session.get(
                    self.url,
                    headers=headers,
                    timeout=15,
                    allow_redirects=True
                )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            with self.lock:
                self.results.append({
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'content_length': len(response.content),
                    'timestamp': datetime.now(),
                    'user_agent': headers['User-Agent'][:50] + '...',
                    'x_forwarded_for': headers['X-Forwarded-For']
                })
            
            return True
            
        except Exception as e:
            with self.lock:
                self.results.append({
                    'status_code': 0,
                    'response_time': 0,
                    'content_length': 0,
                    'error': str(e)[:100],  # Truncate long errors
                    'timestamp': datetime.now(),
                    'user_agent': 'Error',
                    'x_forwarded_for': 'Error'
                })
            return False
    
    def flood_worker(self):
        """Flood mode - continuous requests without delay"""
        for _ in range(self.requests_per_thread):
            self.make_request()
            # No delay in flood mode
    
    def normal_worker(self):
        """Normal mode worker with delay"""
        for i in range(self.requests_per_thread):
            self.make_request()
            if i < self.requests_per_thread - 1:
                time.sleep(self.delay_between_requests)
    
    def worker_thread(self):
        """Worker function for each thread"""
        if self.flood_mode:
            self.flood_worker()
        else:
            self.normal_worker()
    
    def run_test(self):
        """Run the enhanced load test"""
        mode = "FLOOD MODE" if self.flood_mode else "NORMAL MODE"
        scraper_type = "CloudScraper" if self.use_cloudscraper else "Requests"
        
        print(f"🚀 Starting enhanced load test on {self.url}")
        print(f"📊 Mode: {mode} | Scraper: {scraper_type}")
        print(f"🔧 Config: {self.num_threads} threads × {self.requests_per_thread} requests")
        print(f"📈 Total requests: {self.num_threads * self.requests_per_thread}")
        print(f"⏱️  Delay: {self.delay_between_requests}s (ignored in flood mode)")
        print("=" * 70)
        
        start_time = time.time()
        
        # Create and start threads
        threads = []
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.worker_thread)
            threads.append(thread)
            thread.start()
            
            # Small delay between thread starts to avoid overwhelming
            time.sleep(0.001)
        
        # Progress monitoring
        print("🔄 Test in progress...")
        completed_threads = 0
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            completed_threads += 1
            if completed_threads % 10 == 0:
                print(f"   {completed_threads}/{self.num_threads} threads completed")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self.print_enhanced_results(total_time)
    
    def print_enhanced_results(self, total_time):
        """Print enhanced test results and statistics"""
        if not self.results:
            print("❌ No results to display")
            return
        
        successful_requests = [r for r in self.results if 'error' not in r and r['status_code'] == 200]
        failed_requests = [r for r in self.results if 'error' in r or r['status_code'] != 200]
        
        response_times = [r['response_time'] for r in successful_requests]
        
        print(f"\n📋 Enhanced Test Results:")
        print("=" * 70)
        print(f"⏰ Total time: {total_time:.2f} seconds")
        print(f"📊 Total requests: {len(self.results)}")
        print(f"✅ Successful requests: {len(successful_requests)}")
        print(f"❌ Failed requests: {len(failed_requests)}")
        print(f"🎯 Success rate: {(len(successful_requests) / len(self.results) * 100):.2f}%")
        print(f"🚀 Requests per second: {len(self.results) / total_time:.2f}")
        print(f"💥 Peak load: ~{self.num_threads} concurrent connections")
        
        if response_times:
            print(f"\n⚡ Response Time Statistics (ms):")
            print(f"  📊 Average: {statistics.mean(response_times):.2f}ms")
            print(f"  📈 Median: {statistics.median(response_times):.2f}ms")
            print(f"  🏃 Min: {min(response_times):.2f}ms")
            print(f"  🐌 Max: {max(response_times):.2f}ms")
            if len(response_times) > 1:
                print(f"  📏 Std Dev: {statistics.stdev(response_times):.2f}ms")
            
            # Performance categories
            fast = len([t for t in response_times if t < 200])
            medium = len([t for t in response_times if 200 <= t < 1000])
            slow = len([t for t in response_times if t >= 1000])
            
            print(f"\n🚦 Performance Breakdown:")
            print(f"  🟢 Fast (<200ms): {fast} ({fast/len(response_times)*100:.1f}%)")
            print(f"  🟡 Medium (200-1000ms): {medium} ({medium/len(response_times)*100:.1f}%)")
            print(f"  🔴 Slow (>1000ms): {slow} ({slow/len(response_times)*100:.1f}%)")
        
        # Status code distribution
        status_codes = {}
        for result in self.results:
            code = result.get('status_code', 0)
            status_codes[code] = status_codes.get(code, 0) + 1
        
        print(f"\n🔢 Status Code Distribution:")
        for code, count in sorted(status_codes.items()):
            if code == 0:
                print(f"  ❌ Network errors: {count}")
            elif code == 200:
                print(f"  ✅ HTTP {code}: {count}")
            elif 300 <= code < 400:
                print(f"  🔄 HTTP {code}: {count}")
            elif 400 <= code < 500:
                print(f"  ⚠️  HTTP {code}: {count}")
            elif code >= 500:
                print(f"  💥 HTTP {code}: {count}")
        
        # User agent distribution (top 3)
        user_agents = {}
        for result in self.results:
            ua = result.get('user_agent', 'Unknown')
            user_agents[ua] = user_agents.get(ua, 0) + 1
        
        print(f"\n🤖 Top User Agents Used:")
        for ua, count in sorted(user_agents.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"  • {ua}: {count} requests")
        
        # Show errors if any
        if failed_requests:
            print(f"\n🚨 Error Analysis (first 5):")
            for i, result in enumerate(failed_requests[:5]):
                if 'error' in result:
                    print(f"  {i+1}. {result['error']}")
                else:
                    print(f"  {i+1}. HTTP {result['status_code']}")

def main():
    """Main function with enhanced user input"""
    print("🌟 Enhanced Website Load Testing Tool")
    print("🔧 Optimized for Termux with Advanced Features")
    print("=" * 50)
    
    # Get user input
    url = input("🌐 Enter the website URL to test: ").strip()
    
    try:
        print("\n⚙️  Configuration Options:")
        threads = int(input("🧵 Number of concurrent threads (default 50): ") or "50")
        requests_per_thread = int(input("📈 Requests per thread (default 100): ") or "100")
        
        use_cloudscraper = input("☁️  Use CloudScraper for better bypass (y/n, default y): ").lower().strip()
        use_cloudscraper = use_cloudscraper != 'n'
        
        flood_mode = input("💥 Enable flood mode (no delays) (y/n, default n): ").lower().strip()
        flood_mode = flood_mode == 'y'
        
        if not flood_mode:
            delay = float(input("⏱️  Delay between requests in seconds (default 0.01): ") or "0.01")
        else:
            delay = 0
        
    except ValueError:
        print("❌ Invalid input, using default values")
        threads = 50
        requests_per_thread = 100
        delay = 0.01
        use_cloudscraper = True
        flood_mode = False
    
    # Confirm the test
    total_requests = threads * requests_per_thread
    mode = "FLOOD MODE" if flood_mode else "NORMAL MODE"
    
    print(f"\n🎯 Test Summary:")
    print(f"  Target: {url}")
    print(f"  Mode: {mode}")
    print(f"  Total requests: {total_requests}")
    print(f"  Concurrent threads: {threads}")
    print(f"  CloudScraper: {'Yes' if use_cloudscraper else 'No'}")
    
    confirm = input(f"\n⚠️  This will send {total_requests} requests. Continue? (y/n): ").lower().strip()
    
    if confirm != 'y':
        print("❌ Test cancelled")
        return
    
    # Install check
    try:
        import cloudscraper
    except ImportError:
        print("📦 Installing required packages...")
        import subprocess
        subprocess.run(['pip', 'install', 'cloudscraper', 'requests'], check=True)
        import cloudscraper
    
    # Run the test
    try:
        tester = AdvancedWebsiteLoadTester(
            url, threads, requests_per_thread, delay, use_cloudscraper, flood_mode
        )
        tester.run_test()
        
        print(f"\n✅ Test completed successfully!")
        print("💡 Tip: Monitor your server logs to analyze the impact")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Error running test: {e}")

if __name__ == "__main__":
    main()
