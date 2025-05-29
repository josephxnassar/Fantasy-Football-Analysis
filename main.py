import config  # Required
import argparse
from source.app import App
from source.web_interface import run_web_interface

def main():
    parser = argparse.ArgumentParser(description='Fantasy Football Analysis Tool')
    parser.add_argument('--web', action='store_true', help='Run web interface')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the web interface on')
    parser.add_argument('--port', type=int, default=8080, help='Port to run the web interface on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    if args.web:
        print(f"Starting web interface at http://{args.host}:{args.port}")
        run_web_interface(host=args.host, port=args.port, debug=args.debug)
    else:
        a = App()
        # a.run()
        # a.save()
        a.load()
        a.output()

if __name__ == '__main__':
    main()