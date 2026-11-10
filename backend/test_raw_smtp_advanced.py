import smtplib
import sys

def test_raw_smtp(host, port, connect_host):
    print(f"Connecting to {host}:{port} via {connect_host}...")
    try:
        # Pass source_address to force it to use specific interface if needed, or connect directly to connect_host
        server = smtplib.SMTP(connect_host, port, timeout=10)
        server.set_debuglevel(1)
        
        print("Sending EHLO...")
        server.ehlo()
        
        print(f"Raw SMTP test SUCCESS for {connect_host}:{port}")
        server.quit()
    except Exception as e:
        print(f"Raw SMTP test FAILED for {connect_host}:{port}: {e}")

if __name__ == "__main__":
    test_raw_smtp("email-smtp.us-east-1.amazonaws.com", 2587, "email-smtp.us-east-1.amazonaws.com")
    
    ips = ["54.157.237.25", "52.206.145.59", "3.224.1.122"]
    for ip in ips:
        test_raw_smtp("email-smtp.us-east-1.amazonaws.com", 587, ip)
