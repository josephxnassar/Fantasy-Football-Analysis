import config # Required
from app import App

def main():
    app = App(False)
    # app.run()
    # app.save()
    app.load()
    app.output()

if __name__ == '__main__':
    main()