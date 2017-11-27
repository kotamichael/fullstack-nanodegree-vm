import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

## import CRUD Operations ##
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

#Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			if self.path.endswith("/restaurants"):
				restaurants = session.query(Restaurant).all()  					
				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body>"
				output += "</br><a href='/restaurants/new'>Make a new restaurant!</a>"
				output += " <h1> Here are all the restaurants! </h1> "
				for restaurant in restaurants:
					output += "<h3> %s </h3>" % restaurant.name
					output += "<a href ='/restaurants/%s/edit'>Edit</a></br>" % restaurant.id
					output += "</br><a href ='/restaurants/%s/delete'>Delete</a>" % restaurant.id
				output += "</body></html>"

				self.wfile.write(output)

			if self.path.endswith("restaurants/new"):
				restaurantIDPath = self.path.split("/")[2]

				self.send_response(200)
				self.send_header('Content-type', 'text/html')
				self.end_headers()

				output = ""
				output += "<html><body><a href='/restaurants'>Home Page</a>"
				output += "<h1>Make a new restaurant!</h1>"
				output += "<form method='POST' enctype='multipart/form-data' action='/   \
					restaurants/new'>"
				output += "<input name='newRestaurantName' type='text'                   \
					placeholder='New Restaurant Name'>"
				output += "<input type='submit' value='Create'></form>"
				output += "</body></html>"

				self.wfile.write(output)

			if self.path.endswith("/edit"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id \
					= restaurantIDPath).one()
				restaurant = myRestaurantQuery
				if myRestaurantQuery != [] :
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()

					output = ""
					output += "<html><body><a href='/restaurants'>Home Page</a>"
					output += "<h1>Rename %s </h1>" % restaurant.name
					output += "<form method='POST' enctype='multipart/form-data' action='/   \
						restaurants/%s/edit'>" % restaurant.id
					output += "<input name='editName' type='text'                   \
						placeholder='New Restaurant Name'>"
					output += "<input type='submit' value='Update'></form>"
					output += "</body></html>"

					self.wfile.write(output)

			if self.path.endswith("/delete"):
				restaurantIDPath = self.path.split("/")[2]
				myRestaurantQuery = session.query(Restaurant).filter_by(id \
					= restaurantIDPath).one()
				restaurant = myRestaurantQuery
				if myRestaurantQuery != [] :
					self.send_response(200)
					self.send_header('Content-type', 'text/html')
					self.end_headers()

					output = ""
					output += "<html><body><a href='/restaurants'>Home Page</a>"
					output += "<h1>Are you sure you want to delete %s?</h1>" \
						% restaurant.name
					output += "<form method='POST' enctype='multipart/form-data' \
						action='/restaurants/%s/delete'>" % restaurant.id
					output += "<input type='submit' value='Delete'></form>"

					output += "<form method='POST' enctype='multipart/form-data' \
						action='/restaurants/%s/delete'>" % restaurant.id
					output += "<input type='submit' value='NO!'>"
					output += "</form>"
					output += "</body></html>"

					self.wfile.write(output)

		except IOError:
			self.send_error(404, "File Not Found %s" % self.path)

	def do_POST(self):
		try:
			if self.path.endswith("/delete"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				restaurantIDPath = self.path.split("/")[2]

				myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
				
				if myRestaurantQuery != [] :
					session.delete(myRestaurantQuery)
					session.commit()

					self.send_response(301)
					self.send_header('Content-type', 'text/html')
					self.send_header('Location', '/restaurants')
					self.end_headers()

			if self.path.endswith("/edit"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('editName')
				restaurantIDPath = self.path.split("/")[2]

				myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
				if myRestaurantQuery != [] :
					myRestaurantQuery.name = messagecontent[0]
					session.add(myRestaurantQuery)
					session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()

				return

			if self.path.endswith("restaurants/new"):
				ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
				if ctype == 'multipart/form-data':
					fields=cgi.parse_multipart(self.rfile, pdict)
				messagecontent = fields.get('newRestaurantName')

				#Create new Restaurant class
				newRestaurant = Restaurant(name=messagecontent[0])
				session.add(newRestaurant)
				session.commit()

				self.send_response(301)
				self.send_header('Content-type', 'text/html')
				self.send_header('Location', '/restaurants')
				self.end_headers()

				return
		except:
			pass

def main():
	try:
		port = 8080
		server = HTTPServer(('',port), webserverHandler)
		print "Web server running on port %s" % port
		server.serve_forever()

	except KeyboardInterrupt:
		print "^C entered, stopping web server..."
		server.socket.close()

if __name__ == '__main__':
	main()