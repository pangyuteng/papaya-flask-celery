from app import app

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-host',type=str,default='0.0.0.0')
    parser.add_argument('-port',type=int,default='5555')
    args = parser.parse_args()
    app.run(host=args.host,port=args.port)