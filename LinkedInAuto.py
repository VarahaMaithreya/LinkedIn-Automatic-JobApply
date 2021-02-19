import time
import json
import pickle
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import datetime as dt
import keyboard
import win32api, win32con
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import datetime as dt
import os


def emailSender(user, password, receiver, subject, df):
    try:
       
        msg = MIMEMultipart('alternative')   #usually it is alternative   
        msg['Subject'] = subject
        msg['From'] =user
        msg['To'] = receiver
        df_html = df.to_html() 
        part2 = MIMEText(df_html, 'html')
        msg.attach(part2) #to attach parts to the container
              
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)

        
        server.sendmail(user, recipient, msg.as_string())
        server.close()

        print('mail sent bhayya')

    except Exception as e:
        print(str(e))
        print("mail fail ayindi susko malla")



class linkedinEasyApply:
    """
    phone: phone number; userName: LinkedIn username; password: LinkedIn pwd; driverPath: webdriverPath; ResumeLocation: Resume Path.
    
    """
    def __init__(self, phone, username, password, driverPath, jobTitle, state, resumeLocation, role, num_loops, follow_company=None, city=None):
        self.username = username
        self.password = password
        self.driverPath = driverPath
        self.city = city
        self.state = state
        self.jobTitle = jobTitle
        self.resumeLocation = resumeLocation
        self.phone = phone
        self.num_loops = num_loops
        self.role = role
        
        remote = "yes"

        if follow_company:
            self.follow_company = "Yes"
            
        
        self.remote = remote

        self.currentPageJobsList = []
        self.allEasyApplyJobsList=[]
        self.failedEasyApplyJobsList=[]
        self.appliedEasyApplyJobsList=[]

    def url_generator(self):
        #url generator 
        
        
        base = "https://www.linkedin.com/jobs/search/?"
        
        if remote:
          base = "https://www.linkedin.com/jobs/search/?f_CF=f_WRA"
        role = self.role.replace(" ","%20")+"&keywords="
        
        jobTitle = self.jobTitle.replace(" ","%20")+"&location="
        
        state = self.state.replace(" ","%20")

        if self.city:
            city = self.city.replace(" ","%20")+"%2C%20"
            url = base+jobTitle+city+state+"&start=30"
        else:
            url = base + role + jobTitle + state + "&start=30"

        print(url)
        return url

    def click(self, x,y):
        """Mouse event click for webdriver"""
        win32api.SetCursorPos((x,y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

    def init_driver(self):
        """Initializes instance of webdriver"""
        self.driver = webdriver.Chrome(executable_path=self.driverPath)
        self.driver.wait = WebDriverWait(self.driver, 10)
        return self.driver

    def login(self):
        """Logs into LinkedIn.com"""
        self.driver.get("https://www.linkedin.com/")
        try:
            user_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'login-email')))

            pw_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'login-password')))

            login_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, 'login-submit')))

            user_field.send_keys(self.username)
            user_field.send_keys(Keys.TAB)
            time.sleep(random.uniform(2.22, 7.00))
            pw_field.send_keys(self.password)
            time.sleep(random.uniform(1.22, 7.00))
            login_button.click()
        except TimeoutException:
            print("Timeout Vachindi! Username Pwd kanapadaled")

    def searchJobs(self):
        
        url = self.url_generator()
        self.driver.get(url)
        time.sleep(3)

        
        submit_btn = self.driver.find_elements_by_class_name('jobs-search-box__submit-button')
        submit_btn[1].click()
        time.sleep(1)

        dicts = []

        print(int(self.num_loops))
        for x in range(0, int(self.num_loops)):
            pane = self.driver.find_element_by_class_name("jobs-search-results")

            # start from your target element, here for example, "header"
            all_li = pane.find_elements_by_tag_name("li")

            try:
                for x in all_li:
                    all_children_by_xpath = x.find_elements_by_xpath(".//*")

                    try:
                        
                        link = x.find_element_by_class_name("jobs-search-results__list-item")
                        tag = link.get_attribute("href") 
                        link = "https://www.linkedin.com/" + tag
                        jobtitle = x.find_element_by_class_name("job-card-search__title").text
                        location = x.find_element_by_class_name("job-card-search__location").text
                        location = location.splitlines()[1]

                        company = x.find_element_by_class_name("job-card-search__company-name").text

                        #Set easy apply to true by default
                        easy_bool = True

                        #If not found then set easy bool to false
                        try:
                            easyapply = x.find_element_by_class_name("job-card-search__easy-apply")
                        except:
                            easy_bool = False

                        #If true apply to job
                        if easy_bool == True:
                            if tag:
                                self.apply_to_job(tag)
                                status = True
                            else:
                                status = False
                        else:
                            status = False

                        l = []
                        # generate dictionary for reporting
                        values = [company, jobtitle, location, easy_bool, status, link ]
                        for v in values:
                            l.append(v)
                        dicts.append(l)

                    except Exception as e:
                        print(str(e))
                        pass

                
                """
                    For future implementation: pagination (incomplete logic) #thittukoku
                    try:
                    next_button = WebDriverWait(self.driver, 10).until(
                     EC.presence_of_element_located((By.CLASS_NAME, 'artdeco-pagination__indicator')))
                     currentPageCheck = driver.find_element_by_class_name("a11y-text").text
                    self.driver.execute_script("arguments[0].click();", next_button)

                except Exception as e:
                    print(str(e))"""

            except Exception as e:
                print(str(e))

        self.driver.quit()

        return dicts

    def answerForm(self):
        try:
            #Here we need to account for different application windows
            time.sleep(1)
            try:
                phone_input = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/div/form/div/div/div[3]/div[2]/div/div/input')))
                phone_input.clear()
                phone_input.send_keys(self.phone)
                time.sleep(random.uniform(2.22, 4.00))
            except Exception as e:
                print(str(e))

            try:
                form_next_btn = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/div/form/footer/div[2]/button')))
                form_next_btn.click()
            except Exception as e:
                print(str(e))
            
            
            try:
                resumeBtn = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'js-jobs-document-upload__container')))
                resumeBtn.send_keys(self.resumeLocation)
                time.sleep(random.uniform(2.22, 4.00))
            except Exception as e:
                print(str(e))

            try:
                reviewBtn = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/div/form/footer/div[2]/button[2]')))
                reviewBtn.click()
                time.sleep(random.uniform(2.22, 4.00))
            except Exception as e:
                print(str(e))
            
            try:
                form_submit_btn = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div/div/div[2]/div/div[2]/footer/div[3]/button[2]')))
                form_submit_btn.click()
            except Exception as e:
                print(str(e))

            print("Successfully applied to job!")
            time.sleep(random.uniform(1.22, 3.00))

        except:
            print("Form Invalid...recheck the paths")
            


    def apply_to_job(self, url):
        #Get main window
        current_window = self.driver.current_window_handle
        self.driver.execute_script('window.open(arguments[0]);', url)

        #Go to app window
        new_window = [window for window in self.driver.window_handles if window != current_window][0]
        self.driver.switch_to.window(new_window)

        #Set init status
        status = False

        #Look for easy apply button
        try:
            easyApplyBtn = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'job-card-search__easy-apply')))
            easyApplyBtn.click()

            try:
                self.answerForm()
                status = True
            except:
                status = False

        except:
            print("You have already applied to this job!")
            time.sleep(3)

        # Execute required operations to switch back
        self.driver.close()
        self.driver.switch_to.window(current_window)

        return status


    def saveReportAsCSV(df):
     saved_df = pd.DataFrame(df)
     saved_df.columns = ["Company Name", "Job Title", "Location", "Easy Apply", link ,  "Application Successful"]

     path = os.path.join(os.path.expanduser("~"),"Desktop","LinkedIn Auto Applications")
     if not os.path.exists(path):
         os.makedirs(path)

     datestr = dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
     x = 'LinkedIn Applications {}.csv'.format(datestr)

     saved_df.to_csv(os.path.join(path, x), index=False)

     return saved_df