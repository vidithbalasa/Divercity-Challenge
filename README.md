## LinkedIn Employee Extraction and Gender eStimation (LEEGS)
## Installation 
```
$ pip install leegs  
```
#### See Options 
```
$ leegs --help  
```
## Run Challenges 1 & 2 for 20 employees
```
$ leegs hubspot -at 20
```
## How It Works  
Leegs is a powerful tool that allows you to scrape LinkedIn profiles and then uses AI to guess the gender of the employees. This can be extremely useful in diversity hiring initiatives. It completes the job by breaking it into smaller tasks, like an assembly line. First, leegs goes to the profile page of the company scrapes the links to the profiles of all their employees that have public profiles on LinkedIn. Then, it uses multiple threads to crawl the profile links concurrently and extract employee information. Finally, it sends the profile pictures from each employee that had one through an open source gender detection software, DeepFace (a smaller open source one, not the Meta one).  
Under the hood, the majority of the speedups come from `employee_scraper.py` where it runs browsers in various threads in order to speed up employee data extraction. By splitting up the employee load between threads, they can each log in to a different account making sure none of them get flagged. This allows me to keep extracting lots of data without needing loads of accounts. In the case that an account does get banned, the thread is removed and the profile links it couldn't crawl are spread among the other threads. This ensures that leegs can always complete the job, even if there's a faulty piece.  
The image prediction model used is called DeepFace. It is a tool to create image detection models or use pre-trained ones. I chose to use retina net. It is a Convolutional neural network that is trained on over a million images with over 1000 different people to predict if an image is of a male or female. The model outputs a prediction for each image and the leegs scraper keeps track of the gender output for each employee.   
## Full CLI functionality  
#### get info & gender detection on one employee 
```
$ leegs employee -al https://www.linkedin.com/in/<employeeID> -p photos  #### get hubspot employee data for 20 employees without downloading their profile pics 
```
#### crawl through a file of profile links must be a .txt file 
```
$ leegs employee -f filename.txt -p photos LinkedIn Profile Scraper & Gender Classification
```
