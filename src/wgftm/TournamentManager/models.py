from django.db import models
from django.contrib.auth.models import User
import datetime
from TournamentManager.exceptions import NoMatchesInTourney, TourneyMalformed

GENDER_CHOICES = (
                  (u'M', u'Male'),
                  (u'F', u'Female'),
                  (u'?', u'Prefer not to answer')
                  )

# Referal: how people found out about the event
class Referal(models.Model):
    description = models.CharField(max_length=255)
    alwaysShow = models.BooleanField()
    def __unicode__(self):
        return self.description

#
# Personel/attendee level models:
#

# Attendee: someone who goes to WGF
# first name, last name, e-mail, login/password fields are already included
class Attendee(models.Model):
    user = models.OneToOneField(User)
    isUcsd = models.BooleanField()                        # Is the attendee a UCSD student?
    isSixth = models.BooleanField()                       # Is this attendee from Sixth?
    gender = models.CharField(max_length=30, choices=GENDER_CHOICES)    # What is this attendee's gender?
    referals = models.ManyToManyField(Referal, null=True, blank=True)            # How did this attendee hear about WGF?
    def isPlayer(self):                                   # Is the attendee also a player?
        if Player.objects.filter(user=self.user):
            return True
        else:
            return False
    
    def __unicode__(self):
        return "User: " + self.user.username + " | Name: " + self.user.first_name + " " + self.user.last_name

# Guest: a user who is not a player
class Guest(Attendee):
    
    def __unicode__(self):
        return super(Guest, self).__unicode__()

# Player: A user who is a player in the Event.
class Player(Attendee):
    phoneNumber = models.CharField(max_length=10, blank=True)          # Optional field
    #isBusy = models.BooleanField()                        # Is the player CURRENTLY busy - may be used for something
    
    def __unicode__(self):
        return super(Player, self).__unicode__()

#   
# Event level models:
#

# TL: The PRIMARY administrator/s of the tournament
class TournamentLeader(models.Model):
    user = models.OneToOneField(User)
    contact = models.CharField(max_length=255)        # Aggregate contact information here
    def __unicode__(self):
        return self.user.__unicode__()
   
# TA: Someone who administrates a tournament, but does not make the primary
# decisions. A lackey.
class TournamentAssistant(models.Model):
    user = models.OneToOneField(User)
    superior = models.ManyToManyField(TournamentLeader)   # Who is the TL for this person?
    contact = models.CharField(max_length=255)            # Aggregate contact information here
    def __unicode__(self):
        return self.user.__unicode__()

# Event: The highest level of the Tournament. 
class Event(models.Model):
    name = models.CharField(max_length=255)               # The name of the tournament.
    def __unicode__(self):
        return self.name
   
# Checkins of an attendee at an event
class Checkin(models.Model):
    attendee = models.ForeignKey(Attendee)              # The person who checked in
    event = models.ForeignKey(Event)                    # The event checked into
    date = models.DateField(default=datetime.date.today)    # The day checked in
    def __unicode__(self):
        return self.attendee.user.first_name + " " + self.attendee.user.last_name

# Tournament: a tournament for a single game.
class Tournament(models.Model):
    event = models.ForeignKey(Event)                      # What Event does this Tournament belong to?
    name = models.CharField(max_length=255)               # Tournament name
    date = models.DateTimeField()                         # Tournament date
    curNumTeams = models.IntegerField()                   # What is the current number of teams in this tournament?
    maxNumTeams = models.IntegerField()                   # The maximum number of teams in this tournament?
    maxTeamSize = models.IntegerField()                   # What is the maximum number of players on a team in this tournament?
    tournamentLeaders = models.ManyToManyField(TournamentLeader)         # Who are the TLs?
    tournamentAssistants = models.ManyToManyField(TournamentAssistant, null=True, blank=True)   # Who are the TAs?
    prizes = models.CharField(max_length=500)             # Textfield for prizes
    isSeededByRank = models.BooleanField()                # Is this tournament seeded according to rank (metadata)?
#    bracket = models.CharField(max_length=1024)           # Bracket field - contains a string describing the current state/structure of the tournament
    playersIn = models.ManyToManyField(Player)            # What Players are in the Tournament?
    chatChannel = models.CharField(max_length=30)         # What chat channel in-game should players join?
    def __unicode__(self):
        return self.event.name + " " + self.name
        
    #
    # getMatchTiers - returns a in-order list of match tiers - 
    #                 i.e.: [finals, semifinals, quarterfinals... pool play/first level of the bracket]
    #                 which can be interated over in a template to display the tournament structure
    # raises: NoMatchesInTourneyError, TourneyMalformedError
    def getMatchTiers():
        matches = Match.objects.filter(tournament=t)
        if not matches:
            raise NoMatchesInTourney()
      
        # Find root match (i.e.: the final game, has no parent matches)
        root = None
        for match in matches:
            if match.matchWinners is None and match.matchLosers is None:
                root = match
                matches = matches.exclude(id=root.id)
                break
      
        if root is None:
            raise TourneyMalformed()
        tiers = []
        curLevel = []
        level.append(root)
        # Append a copy of the current level to tiers.
        tiers.append(list(curLevel))
        prevLevel = list(curLevel)
        # While we haven't placed every match into a tier
        while not matches:
            prevLevel = list(curLevel)
            curLevel = []
            for match in prevLevel:
                winnerMatches = Match.objects.filter(matchWinners=match)
                loserMatches = Match.objects.filter(matchLosers=match)
                curLevel.append( winnerMatches )
                curLevel.append( loserMatches )
                matches = matches.exclude(matchWinners=match)
                matches = matches.exclude(matchLosers=match)
            tiers.append( list(curLevel) )
        return tiers


# Team: Can be a single player or a collection of players, but ONLY teams are part of Games. The participants
# in a game
class Team(models.Model):
    name = models.CharField(max_length=30)                               # What is the name of this team?
    tournament = models.ForeignKey(Tournament)                           # What tournament is this team playing in?
    numOfPlayers = models.IntegerField()                                 # How many players are on this team?
    players = models.ManyToManyField(Player, related_name = 'players')   # What players are on the this team?
    captain = models.ForeignKey(Player, related_name = 'captain')        # Who is the team captain? 
    metadata = models.IntegerField(null=True, blank=True)                # Data for matchmaking - if a matchmaking algorithm is specified, use this to determine rankings
    def __unicode__(self):
        return self.tournament.__unicode__() + ": " + self.name

# Match: single Match for the tournament (one node of the tournament) - a Match can consist of many games
class Match(models.Model):
    tournament = models.ForeignKey(Tournament)            # What tournament does this match belong to?
    description = models.CharField(max_length=64)         # What is this match's description? 
    teams = models.ManyToManyField(Team, null=True, blank=True)                  # What teams are participaiting?
    winnerParent = models.OneToOneField('self', related_name = '+', verbose_name = 'match for winners', null=True, blank=True)   # Where should the winners go?
    loserParent = models.OneToOneField('self', related_name = '+', verbose_name = 'match for losers', null=True, blank=True)     # Where should the losers go?
    matchWinners = models.ManyToManyField(Team, related_name = 'matchWinners', verbose_name = 'teams who won the match', null=True, blank=True) # Who are the winners?
    matchLosers = models.ManyToManyField(Team, related_name = 'matchLosers', verbose_name = 'teams who lost the match', null=True, blank=True)  # Who are the losers?
    def __unicode__(self):
        return self.tournament.__unicode__() + ": " + self.description

# Results: results of all teams in a game
class Result(models.Model):
    team = models.ForeignKey(Team)   # The team whose score is here
    score = models.IntegerField()    # The score of the team
    def __unicode__(self):
        return self.score.__str__()

# Games: a Match consists of any number of games
# CAN support round robin/pool play.
class Game(models.Model):
    match = models.ForeignKey(Match)                                  # The Match the Game is associated with
    teams = models.ManyToManyField(Team, related_name = 'teams')      # Who are the teams in this game (may be more than just 2)
    verified = models.BooleanField()                                  # Has the game been verified?
    startTime = models.TimeField()                                    # When should the game start?
    gameWinners = models.ManyToManyField(Team, related_name = 'gameWinners', verbose_name = 'teams who won the game')  # Who were the winners?
    gameLosers = models.ManyToManyField(Team, related_name = 'gameLosers', verbose_name = 'teams who lost the game')    # Who were the losers?
    results = models.ManyToManyField(Result)                          # Score results of teams in this game
    def __unicode__(self):
        return self.match.__unicode__() + ": " + self.name
