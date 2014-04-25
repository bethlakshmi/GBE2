# 
# models.py - Contains Django Database Models for Ticketing - Defines Database Schema
# edited by mdb 4/25/2014
#

# python manage.py sql ticketing

from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class TicketItem(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    active = models.BooleanField(default=False)
    cost = models.DecimalField(max_digits=20, decimal_places=2)
    linked_events = models.ManyToManyField('gbe.Event')
    datestamp = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User)

    def __unicode__(self):
        return self.title
    

'''
-- --------------------------------------------------------

--
-- Table structure for table `BPTEventList`
--

DROP TABLE IF EXISTS `BPTEventList`;
CREATE TABLE IF NOT EXISTS `BPTEventList` (
  `BPTEvent` varchar(30) NOT NULL,
  `Primary` tinyint(1) NOT NULL,
  `ActSubmitFee` tinyint(1) NOT NULL,
  PRIMARY KEY (`BPTEvent`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `BPTSettings`
--

DROP TABLE IF EXISTS `BPTSettings`;
CREATE TABLE IF NOT EXISTS `BPTSettings` (
  `DeveloperID` varchar(30) NOT NULL,
  `ClientID` varchar(30) NOT NULL,
  `LastPollTime` datetime NOT NULL,
  PRIMARY KEY (`DeveloperID`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

'''

'''    
--
-- Table structure for table `Transactions`
--

DROP TABLE IF EXISTS `Transactions`;
CREATE TABLE IF NOT EXISTS `Transactions` (
  `TransIndex` int(11) NOT NULL AUTO_INCREMENT,
  `ItemId` varchar(30) NOT NULL,
  `UserId` int(11) NOT NULL,
  `Amount` double(10,2) NOT NULL,
  `Datestamp` datetime NOT NULL,
  `PaymentDate` datetime NOT NULL,
  `PaymentSource` varchar(30) NOT NULL,
  `Status` enum('Posted','Settled','Voided','Error') NOT NULL,
  `TenderType` enum('Cash','Check','Charge','Comp') NOT NULL,
  `Reference` varchar(30) NOT NULL,
  `Cashier` int(11) DEFAULT NULL,
  `Memo` varchar(500) NOT NULL,
  `Override` tinyint(1) NOT NULL,
  PRIMARY KEY (`TransIndex`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=10 ;

'''

'''
--
-- Table structure for table `LimboTransactions'
--

DROP TABLE IF EXISTS `LimboTransactions`;
CREATE TABLE IF NOT EXISTS `LimboTransactions` (
  `LimboIndex` int(11) NOT NULL AUTO_INCREMENT,
  `FirstName` varchar(30) NOT NULL,
  `LastName` varchar(30) NOT NULL,
  `PaymentEmail` varchar(64) NOT NULL,
  `Country` varchar(30) NOT NULL,
  `Phone` varchar(30) NOT NULL,
  `ItemId` varchar(30) NOT NULL,
  `Amount` double(10,2) NOT NULL,
  `PaymentDate` datetime NOT NULL,
  `PaymentSource` varchar(30) NOT NULL,
  `Status` enum('Posted','Settled','Voided','Error') NOT NULL,
  `TenderType` enum('Cash','Check','Charge','Comp') NOT NULL,
  `Reference` varchar(30) NOT NULL,
  `TrackerId` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`LimboIndex`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
'''

