import config # Required
from source.app import App

def main():
    a = App()
    # a.run()
    # a.save()
    a.load()
    a.output()

if __name__ == '__main__':
    main()