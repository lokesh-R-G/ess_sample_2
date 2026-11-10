import smtplib
import ssl

def test_raw_smtp():
    host = "email-smtp.us-east-1.amazonaws.com"
    port = 587
    
    print(f"Connecting to {host}:{port}...")
    try:
        server = smtplib.SMTP(host, port, timeout=10)
        server.set_debuglevel(1)
        
        print("Sending EHLO...")
        server.ehlo()
        
        print("Starting TLS...")
        context = ssl.create_default_context()
        server.starttls(context=context)
        
        print("Sending post-TLS EHLO...")
        server.ehlo()
        
        print("Quitting...")
        server.quit()
        print("Raw SMTP test SUCCESS.")
    except Exception as e:
        print(f"Raw SMTP test FAILED: {e}")

if __name__ == "__main__":
    test_raw_smtp()
