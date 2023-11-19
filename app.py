from app_factory import create_app
import argparse
from plot_diagram import plot_routes_diagram, extract_all_routes

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-diagram", action="store_true", help="Display routes diagram")
    args = parser.parse_args()

    if args.diagram:
        extracted_routes = extract_all_routes()
        plot_routes_diagram(extracted_routes)
    else:
        app = create_app()
        app.run(debug=True)
