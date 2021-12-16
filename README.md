Team Wildebeest Small Group project
Team members
The members of the team are:

Duna Alghamdi, 
Marija Buivyte, 
Yiren Liang,
Jad Sbaï,  
Lilianna Szabo, 

Project structure
The project is a chess-club management system. It has clubs and tournaments. 
A user can apply to a club, then an officer has the choice to deny or to accept the application, which sends a notification to the user.
The user then can join the club. A member of the club can also then leave the club, or can be banned by the owner. The owner can promote and demote officers.

Any officer or the owner can organise a tournament in a club. It has to have between 2 and 96 players to start, but at the time of creation, the organiser can set tighter limits.
Members of the club can then apply and withdraw from tournaments until the deadline. The organiser can also choose a co-officer for the tournament.
Once the deadline is reached, and it has enough participants, the organiser can publish the schedule, then start the tournament. The schedule will automatically be published if the organiser chooses to start the tournament without publishing first. 
The organiser or any co-organiser can enter the results of a match. Once all the matches are completed in a phase, a new phase will automatically start. 
In case of a draw in the elimination system, the players will have to replay the match, until a winner is found. In the group phase, if two or more players have the same amount of points, the advancing two will be chosen randomly. Further improvements could make both of these dependent on the ELO rating system.
The participants can see all their matches in all tournaments.
A user can also see all of their current, past, and upcoming tournaments. 

Deployed version of the application
The deployed version of the application can be found at URL.

Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment. From the root of the project:

$ virtualenv venv
$ source venv/bin/activate
Install all required packages:

$ pip3 install -r requirements.txt
Migrate the database:

$ python3 manage.py migrate
Seed the development database with:

$ python3 manage.py seed
Run all tests with:

$ python3 manage.py test
The above instructions should work in your version of the application. If there are deviations, declare those here in bold. Otherwise, remove this line.

Sources
The packages used by this application are specified in requirements.txt

This projects has code borrowed from the recommended training videos.

