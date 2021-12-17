Team Wildebeest 

The members of the team are:

Duna Alghamdi, 
Marija Buivyte, 
Yiren Liang,
Jad Sbaï,  
Lilianna Szabo, 

Link to the URl of the deployed version of the system:
https://mighty-garden-89605.herokuapp.com/

Link to the URl of the admin interface of the deployed version of the system:
https://mighty-garden-89605.herokuapp.com/admin/

Sources:

1. We completely reused the base code taught by the lecturer for the Clucker application.
2. In order to implement club_specific as well as tournament-specific permissions, we highly inspired ourselves from the following StackOverflow solution: https://stackoverflow.com/questions/69570682/how-to-setup-django-permissions-to-be-specific-to-a-certain-models-instances
3. The packages used by this application are specified in requirements.txt

Project structure:

The project is a chess-club management system. It has clubs that can be created. Inside each club, the officers and owner can create tournaments for the rest of the club to participate in. 
A user can apply to a club, then an officer has the choice to deny or accept the application, which sends a notification to the user.
The user can then join the club. A member of a club can also then leave the club, or can be banned by the owner. The owner can promote members and demote officers.

A tournament must include between 2 and 96 players to start, but at the time of creation, the organiser can set tighter limits.
Members of the club can then apply and withdraw from tournaments until the deadline. The organiser can also assign co-organisers for his tournament(s).
Once the deadline is reached, and it has enough participants, the organiser can publish the schedule and/or start the tournament. The schedule will automatically be published if the organiser chooses to start the tournament without publishing first. 
The organiser or any co-organiser can enter results for matches. Once all the matches are completed in a phase, the next phase will automatically start and its schedule will be published as well.
In case of a draw in the elimination system, the players will have to replay the match, until a winner is determined. In the group phase(s), if two or more players have the same amount of points, the advancing two will be chosen randomly. 
Further improvement: Using of ELO ratings to determine which player goes into the next phase in a fair-and-square way
The participants can see all their upcoming matches in the tournaments they're participating in
A user can also see all of their current, past, and upcoming tournaments. 


Possible further improvements:

There are some things that could have been improved, for instance, class based views, which would allow us to structure the code and reuse code by harnessing inheritance and mixins.
Secondly, writing more thorough tests for template content. 
Thirdly, improve encapsulations of model classes.
Fourthly, refactor the views.py and models.py files into more concise and maintainable directories. Shortening some views by creating supplementary decorators would also improve maintainability
Fifthly, the algorithm for scheduling the matches is not optimal as it randomly selects non-encountered players.
Last but not least, adding sorting filters to users list and clubs list. (Sorting by status for example)

Installation instructions:

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



