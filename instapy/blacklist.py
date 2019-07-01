import os
import csv
import datetime


class Blacklist:

    fieldnames = ['date', 'username', 'campaign', 'action']

    def __init__(self, enabled=False, logfolder='', campaign=False, logger=False):
        self.enabled = enabled
        self.campaign = campaign
        self.logger = logger
        self.file = "{}blacklist.csv".format(logfolder)

    def init(self):
        if self.enabled and not os.path.isfile(self.file):
            self.logger.info('Creating blacklist for Campaign: {}'.format(self.campaign))
            self.create_csv_file()

    def entry_exists(self, username, action):
        with open(self.file, 'r') as file:
            reader = csv.DictReader(file, fieldnames=Blacklist.fieldnames)
            for row in reader:
                if (
                        (action is not None and
                         row['username'] == username and
                         row['campaign'] == self.campaign and
                         row['action'] == action)

                        or

                        (action is None and row['username'] == username)
                ):
                    return True
            return False

    def get_users(self, campaign):
        users = set()
        with open(self.file, 'r') as blacklist:
            reader = csv.DictReader(blacklist, fieldnames=Blacklist.fieldnames)
            for row in reader:
                if row['campaign'] == campaign:
                    users.add(row['username'])
        return users

    def create_csv_file(self):
        with open(self.file, 'a+') as blacklist:
            writer = csv.DictWriter(blacklist, fieldnames=Blacklist.fieldnames)
            writer.writeheader()

    def add_entry(self, username, action):
        try:
            with open(self.file, 'a') as blacklist:
                writer = csv.DictWriter(blacklist, fieldnames=Blacklist.fieldnames)
                writer.writerow({
                    'date': datetime.date.today().strftime('%m/%d/%y'),
                    'username': username,
                    'campaign': self.campaign,
                    'action': action
                })
        except Exception as err:
            self.logger.error('blacklist dictWrite error {}'.format(err))

        self.logger.info('--> {} added to blacklist for {} campaign (action: {})'
                    .format(username, self.campaign, action))

