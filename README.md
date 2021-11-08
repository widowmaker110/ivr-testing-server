# AWS IVR Testing Server
## _Making IVR testing simple_


This is a sister project to [IVR Tester](https://github.com/widowmaker110/ivr-tester). Both are needed to make them work. 

Heavy inspiration taken from https://github.com/SketchingDev/ivr-tester

## Features

- Easy to use JSON inputs for unit tests
- Results logged in local JSON database created for you

## Writing Tests

Tests are broken down into individual JSON files. Three key-value pairings control the phone testing system.

- "expect"
  - array of possible phrases. Twilio converts the audio of the recipient into text the best it can. This is an array because sometimes the ML programming interpretting the audio can return different results with only slight variences. 
- "then"
  - Single string with three options today. null, "say=", and "press=". null means "do nothing". "say=" with say anything after the equals. "press=" will send a DTMF tone to the recipient matching the number. Single digits are only support today
- "timeout"
  - number in seconds how long the Twilio phone should wait for recipient to say or do something.

```sh
[
	{
		"expect":
		[
			"Hello, and welcome to the awesome phone center, press 1 for sales."
		],
		"then": "press=1",
		"timeout": 3
	},
	{
		"expect":
		[
			"who is your favorite programmer?",
			"who is your favorite programmer",
			"Who is your favorite programer?",
			"Who is your favorite programer"
		],
		"then": "say=alan turing",
		"timeout": 3
	}
]
```

**NOTE:** Today, only supports single tests. Working on making it handle all JSON files in testSuite directory

### Reading Test Results

Once the program has finished, you'll see a "db.json" under the "results" directory. This is TinyDB saving the results. You may have to use a Pretier program to see the JSON but the result should look like below:

```sh
{
    "_default":
    {
        "1":
        {
            "unique_id": "30e82350-d05c-4fb1-9c6b-6e1f9fb69f4a",
            "status": "complete",
            "startTimestamp": "2021-11-07T19:40:01.732456",
            "endTimeStamp": null,
            "currentIndex": 0,
            "currentStep": 2,
            "instructions":
            [
                {
                    "file": "testSalesCall.json",
                    "steps":
                    [
                        {
                            "expect":
                            [
                                "Hello, and welcome to the awesome phone center, press 1 for sales."
                            ],
                            "then": "press=1",
                            "timeout": 3
                        },
                        {
                            "expect":
                            [
                                "who is your favorite programmer?",
                                "who is your favorite programmer",
                                "Who is your favorite programer?",
                                "Who is your favorite programer"
                            ],
                            "then": "say=alan turing",
                            "timeout": 3
                        }
                    ]
                }
            ],
            "results":
            [
                {
                    "file": "testSalesCall.json",
                    "step":
                    [
                        "hello, and welcome to the awesome phone center, press 1 for sales."
                    ],
                    "status": "passed"
                },
                {
                    "file": "testSalesCall.json",
                    "step":
                    [
                        "who is your favorite programmer?",
                        "who is your favorite programmer",
                        "who is your favorite programer?",
                        "who is your favorite programer"
                    ],
                    "status": "passed"
                }
            ]
        }
    }
}
```

Under the "results" node, there are several entries recording the status "passed" or "failed". If a step failed, you will see a "actualResult" node below it showing what actually was said. 

## Installation

This project runs on a few stacks to perform its operations.

- [AWS](https://aws.amazon.com/) (Connect phone center)
- [Python](https://www.python.org/downloads/) (logic - built on 3.8)
- [ngrok](https://ngrok.com/) (local server for Twilio to ping during calls)
- [Twilio](https://www.twilio.com/) (programmatic phone handling)
- ✨Magic ✨

In a command line interface, use [NPM](https://www.npmjs.com/) to install ngrok
```sh
npm install grok
```

In this project's directory, install all the libraries to get this running

```sh
pip install -r requirements.txt
```

Buy a Twilio phone number if you don't already have one. [Instructions](https://support.twilio.com/hc/en-us/articles/223135247-How-to-Search-for-and-Buy-a-Twilio-Phone-Number-from-Console). The free trial gives you a number and credit to try. Get the "account_sid" for your account for later. They're located in the account dashboard.

Set up an Amazon Connect instance with a phone number if you haven't already. **NOTE**: These will [cost](https://aws.amazon.com/connect/pricing/). You'll be paying for the phone number (daily rate) and any inbound calls in your region (per use)

Import the contact flow located in the **"aws-connect-contact-flows"** folder and assign it to your phone number. [Create instance](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-instances.html) (**I picked "Store users in Amazon Connect"**), [Assigning Flow to number](https://docs.aws.amazon.com/connect/latest/adminguide/associate-phone-number.html), [Importing Contact Flow](https://docs.aws.amazon.com/connect/latest/adminguide/contact-flow-import-export.html)

**NOTE**: you will not be able to save and publish until you import the Lex bot below.

Create a Lex Bot. The template for this example can be found in the **"aws-lex-bot"** folder [Importing Lex instructions](https://docs.aws.amazon.com/lex/latest/dg/import-from-lex.html). Then you will want to whitelist it to the Connect instance you made before [Instructions](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-lex.html)

## Running Tests

Always start by first running the ngrok program if its not already running
```sh
nrgok http 3000
```

Set the environment file (.env) with the ngrok URL shown in the CLI. Below is an example:
```sh
Session Status                online                                            
Session Expires               1 hour, 59 minutes                                
Version                       2.3.40                                            
Region                        United States (us)                                
Web Interface                 http://127.0.0.1:4040                             
Forwarding                    http://f737-98-27-180-53.ngrok.io -> http://localhost
Forwarding                    https://f737-98-27-180-53.ngrok.io -> http://localhost
```

I'm using [Pycharm](https://www.jetbrains.com/pycharm/) so I just run the project but if you're running CLI commands (in a new tab separate from ngrok):

```sh
python3 main.py
```

Run the sister project after configuring it so it performs an outbound call.

## Roadmap

- Ability to handle multiple test files at once
- Test code coverage

## License

MIT

**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)
