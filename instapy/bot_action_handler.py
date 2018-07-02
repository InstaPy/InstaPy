
from api_db import fetchOne, select, insert
import datetime
import json
from random import randint
import calendar
import bot_util


#todo cleanup the code
def getInitialActionAmount(self, id_campaign):
    result={}
    result['calculatedAmount']={}
    result['initialAmount']={}
    result['accountMaturity']={}
    result['accountMaturity']['reachedMaturity']=False
    result['accountMaturity']['warmingUp']=False
    result['accountMaturity']['startup']=False

    maximumLikeAmountResult = fetchOne("select * from bot_config where `key`='maximum_like_amount'")
    result['initialAmount']['maximumLikeAmount']=int(maximumLikeAmountResult['value'])

    maximumFollowAmountResult = fetchOne("select * from bot_config where `key`='maximum_follow_amount'")
    result['initialAmount']['maximumFollowAmount'] = int(maximumFollowAmountResult['value'])
   
    minimumLikeAmountResult = fetchOne("select * from bot_config where `key`='minimum_like_amount'")
    result['initialAmount']['minimumLikeAmount'] = int(minimumLikeAmountResult['value'])


    minimumFollowAmountResult = fetchOne("select * from bot_config where `key`='minimum_follow_amount'")
    result['initialAmount']['minimumFollowAmount'] = int(minimumFollowAmountResult['value'])

    result['initialAmount']['minimumActionAmount'] = result['initialAmount']['minimumLikeAmount'] +result['initialAmount']['minimumFollowAmount']
    result['initialAmount']['maximumActionAmount'] = result['initialAmount']['maximumLikeAmount'] + result['initialAmount']['maximumFollowAmount']

    
    self.logger.info("getInitialActionAmount: Default bot configuration is: %s ", result)
    

    self.logger.info("getInitialActionAmount: Checking if account is warming up...")

    if isAccountWarmingUp(self)==True:
      result['calculatedAmount']=getWarmUpResult(self, result['initialAmount'], 30)
      result['accountMaturity']['warmingUp']=True
      return result
    
    if isAccountStartup(self)==True:
      result['calculatedAmount']=getWarmUpResult(self, result['initialAmount'], 15)
      result['accountMaturity']['startup']=True
      return result
    

    #check maturity of account
    self.logger.info("getInitialActionAmount: Checking if the account is 100% functional...")
    accountIsFullyFunctionalAfter=90
    campaign = fetchOne("select campaign.timestamp, percentage_amount, month_start,month_end from campaign join instagram_account_type using (id_account_type) where id_campaign=%s", id_campaign)
   
    d0 = campaign['timestamp']
    d1 = datetime.datetime.now()
    delta = d1 - d0
    
    if delta.days>=accountIsFullyFunctionalAfter:
        result['calculatedAmount']=result['initialAmount']
        result['accountMaturity']['reachedMaturity']=True
        self.logger.info("getInitialActionAmount: Account is fullyFunctional ! %s days passed since signup. Minimum is %s" % (delta.days, accountIsFullyFunctionalAfter))
        return result
    else:
        self.logger.info("getInitialActionAmount: Account is not fully functional, going to apply the percentage based on instagram account maturity...")
    
    self.logger.info("getInitialActionAmount: Going to calculated action number based on account type: month_start: %s, month_end:%s, percentage: %s" % (campaign['month_start'],campaign['month_end'], campaign['percentage_amount']))
    result['accountMaturity']['usage_percentage'] = campaign['percentage_amount']
    calculatedAmount = getWarmUpResult(self, result['initialAmount'], campaign['percentage_amount'])
    result['calculatedAmount']=calculatedAmount
    self.logger.info("getInitialActionAmount: After applying %s percentage, the result is: %s" % (campaign['percentage_amount'], result))
    return result
    

def isAccountWarmingUp(self):
    warmUpDays=3
    self.logger.info("getInitialActionAmount: Checking if account is warming up...")
    workedDaysResult = fetchOne("select count(*) as worked_days from (select distinct date(timestamp) from bot_action where id_campaign=%s order by date(timestamp)) worked_days", self.campaign['id_campaign'])
    
    if workedDaysResult['worked_days']<warmUpDays:
      self.logger.info("getInitialActionAmount: The bot warmed  up for %s days so far. This means the bot still needs to warm up until reaches %s days." %  (workedDaysResult['worked_days'], warmUpDays))
      return True
    else:
      self.logger.info("getInitialActionAmount: The bot worked for %s days so far. This means it is fully warmed up ! Minimum %s days to warmup !" % ( workedDaysResult['worked_days'], warmUpDays))
      return False

def isAccountStartup(self):
    self.logger.info("isAccountStartup: Checking if campaign %s is startup...", self.campaign['id_campaign'])
    trialStartupAccount = fetchOne("select id_user from campaign  join user_subscription using (id_user) join plan using(id_plan) join plan_type using (id_plan_type) where id_campaign=%s and name='TRIAL_STARTUP'", self.campaign['id_campaign'])
    self.logger.info("IsAccountStartup result: %s", trialStartupAccount)
    if trialStartupAccount:
      return True
    else:
      return False
      
      
def getWarmUpResult(self, initialAmount, percentageAmount):
  calculatedAmount={}
  
  calculatedAmount['maximumLikeAmount']= int(round(initialAmount['maximumLikeAmount'] * percentageAmount / 100))
  calculatedAmount['maximumFollowAmount']= int(round(initialAmount['maximumFollowAmount'] * percentageAmount / 100))
  calculatedAmount['minimumLikeAmount']= int(round(initialAmount['minimumLikeAmount'] * percentageAmount / 100))
  calculatedAmount['minimumFollowAmount']= int(round(initialAmount['minimumFollowAmount'] * percentageAmount / 100))
  calculatedAmount['minimumActionAmount'] = initialAmount['minimumLikeAmount'] + calculatedAmount['minimumFollowAmount']
  calculatedAmount['maximumActionAmount'] = initialAmount['maximumLikeAmount'] + calculatedAmount['maximumFollowAmount']
  
  return calculatedAmount
    

#this function is used to retrieve the configuration if it is stoped and restarted
def resumeOperation(self, id_campaign):
  self.logger.info("resumeOperation: trying to resume")
  resumeResult = fetchOne("SELECT * FROM campaign_log WHERE DATE(`timestamp`) = CURDATE() and id_campaign=%s",id_campaign)
  
  if resumeResult is None:
    self.logger.info("resumeOperation: Could not resume, going to start from scratch !")
    return None

  self.logger.info("resumeOperation: Checkpoint was found, id: %s ",resumeResult['id_log'])
  result = {}
  self.id_log = resumeResult['id_log']
  result['like_amount']=resumeResult['expected_like_amount']
  result['follow_amount']=resumeResult['expected_follow_amount']
  
  return result

  
def getAmountDistribution(self, id_campaign):
  
    resume = resumeOperation(self,id_campaign)
    
    if resume is not None and resume['like_amount'] is not None and resume['follow_amount'] is not None:
      self.logger.info("getAmountDistribution: going to resume this amount: %s",resume)
      return resume
    
    categories = select("select * from action_amount_distribution")

    foundRightCategory = False
    securityBreak=10
    iteration = 0

    now = datetime.datetime.now()
    currentMonthNumberOfDays =  calendar.monthrange(now.year, now.month)[1]

    initialActionAmountResult = getInitialActionAmount(self, id_campaign)

    #maybe this while can be extracted separately
    while foundRightCategory==False and iteration<securityBreak and len(categories)>0:
        selectedCategoryIndex = randint(0, len(categories) - 1)

        #check if selected category is still available
        daysForThisCategory = int(round(currentMonthNumberOfDays * categories[selectedCategoryIndex]['percentage_amount']/100))

        

        amountToPerform = None
        if categories[selectedCategoryIndex]['type'] == "minimum":
          amountToPerform = "<="+str(initialActionAmountResult['calculatedAmount']['minimumActionAmount'])
          
        elif categories[selectedCategoryIndex]['type'] == "maximum":
          amountToPerform = ">="+str(initialActionAmountResult['calculatedAmount']['maximumActionAmount'])
          
        elif categories[selectedCategoryIndex]['type'] == "between":
          amountToPerform = "between "+str(initialActionAmountResult['calculatedAmount']['minimumActionAmount']) + " and "+str(initialActionAmountResult['calculatedAmount']['maximumActionAmount'])
          
        query = " select count(*) as total from  (select count(*) as total, date(timestamp) from bot_action " \
                " WHERE MONTH(timestamp) = MONTH(CURRENT_DATE()) " \
                " AND YEAR(timestamp) = YEAR(CURRENT_DATE()) and id_campaign=%s " \
                " group by date(timestamp) having count(*) "+amountToPerform + " " \
                " order by date(timestamp) desc) my_table"

        result = fetchOne(query, id_campaign)
        #self.logger.info("getAmountDistribution: %s",query)
        self.logger.info("getAmountDistribution: Selected category: %s, iteration %s, daysForThisCategory: %s, usedDays: %s" % (
        categories[selectedCategoryIndex], iteration, daysForThisCategory, result['total']))

        usedDaysForThisCategory = result['total']
        if result['total']<daysForThisCategory:
          foundRightCategory = categories[selectedCategoryIndex]
          break
        
        iteration = iteration + 1
        del categories[selectedCategoryIndex]
       
    self.logger.info("getAmountDistribution: Choosed category: %s ",foundRightCategory)
    
    result={}
    
    if foundRightCategory['type'] == "minimum":
      result['like_amount'] = initialActionAmountResult['calculatedAmount']['minimumLikeAmount']
      result['follow_amount'] = initialActionAmountResult['calculatedAmount']['minimumFollowAmount']
          
    elif foundRightCategory['type'] == "maximum":
      result['like_amount'] = initialActionAmountResult['calculatedAmount']['maximumLikeAmount']
      result['follow_amount'] = initialActionAmountResult['calculatedAmount']['maximumFollowAmount']
          
    else:
      #between
      result['like_amount'] = randint(initialActionAmountResult['calculatedAmount']['minimumLikeAmount']+1, initialActionAmountResult['calculatedAmount']['maximumLikeAmount']-1)
      result['follow_amount'] = randint(initialActionAmountResult['calculatedAmount']['minimumFollowAmount']+1, initialActionAmountResult['calculatedAmount']['maximumFollowAmount']-1)
    
    #create the log in database
    log={}
    log['amount_selected_category'] = {}
    log['amount_selected_category']['category']=foundRightCategory
    log['amount_selected_category']['daysAllocatedForThisCategory'] = daysForThisCategory
    log['amount_selected_category']['usedDaysForThisCategory'] = usedDaysForThisCategory
    log['amount_selected_category']['currentMonthNumberOfDays'] = currentMonthNumberOfDays
    log['expected_amount']=result
    log['initial_action_amount']=initialActionAmountResult


    logJson = json.dumps(log)

    id = insert("insert into campaign_log (`id_campaign`,`details`, `name`, `expected_like_amount`, `expected_follow_amount`, `id_amount_distribution`, `timestamp`) values (%s,%s,%s,%s,%s,%s,now())",id_campaign,logJson,'LOG_CAMPAIGN_START',result['like_amount'],result['follow_amount'],foundRightCategory['id_amount_distribution'])
    self.id_log=id
    self.logger.info("getAmountDistribution: Final action amount: %s",result)
    self.logger.info("getAmountDistribution: ID_LOG: %s",id)

    return result


def getLikeAmount(self,id_campaign, calculatedAmount):
  likesAmount=calculatedAmount['like_amount']

  return likesAmount

  
  
# there is one strange thing about the follow amount:
# if the user has selected only the unfollow operation, the total follow/unfollow amount should be devided by 2
def getFollowAmount(self,id_campaign, calculatedAmount):
  followAmount=calculatedAmount['follow_amount']

  return followAmount

def getLikesPerformed(self, dateParam):
  likesPerformed=fetchOne('SELECT count(*) as no_op FROM bot_action where bot_operation like %s and date(timestamp)=%s and id_user=%s', "like"+"%", str(dateParam), self.web_application_id_user)
  
  if likesPerformed['no_op'] >0:
    self.logger.info("getLikesPerformed: Campaign id %s has  ALREADY performed %s likes. in day %s" % (self.campaign['id_campaign'], likesPerformed['no_op'], dateParam))
  else:
    self.logger.info("getLikesPerformed: 0 likes PREVIOUSLY performed for campaign id  %s, in day %s" % (self.campaign['id_campaign'],dateParam))
  
  return likesPerformed['no_op']


def getActionAmountForEachLoop(noActions, noLoops):

    if noActions < 1:
        return 0

    actionsPerLoop = noActions // noLoops

    randomizedActionPerLoop = randint(bot_util.randomizeValue(actionsPerLoop,10,"down"), bot_util.randomizeValue(actionsPerLoop,10,"up"))

    return randomizedActionPerLoop

def getFollowPerformed(self,dateParam):
    
  #follows peformed during this day
  followsPerformed=fetchOne("SELECT count(*) as no_op FROM `bot_action` where (bot_operation like %s or bot_operation like %s) and date(timestamp)=%s and id_user=%s", "follow_"+"%","unfollow"+"%", str(dateParam), self.web_application_id_user)
  
  if followsPerformed['no_op'] >0:
    self.logger.info("getFollowAmount: Campaign id %s has ALREADY performed %s follow/unfollow, in day %s ." % (self.campaign['id_campaign'], followsPerformed['no_op'],dateParam))  
  else:
    self.logger.info("getLikesPerformed: 0 follow ALREADY performed for campaign %s, in day %s" % (self.campaign['id_campaign'],dateParam))
  
  return followsPerformed['no_op']