import os, sys, time, csv
import random
import Tkinter, tkFileDialog
from pyglet.media import avbin
from psychopy import sound, visual, logging, event, microphone, gui, core

# ### Variable Dictionary #######################################################################################
#                                                                                                               #
# story: a dictionary containing the story                                                                      #
# sentences: a dictionary containing the sentences                                                              #
# segments: a dictionary containing the segments                                                                #
# wms: a dictionary containing the wms paragraph                                                                #
# path: the path to the folder where the .py file is located. All experimental visuals should be located here   #
#       in a folder called 'Cues'.The recordings and log file for each participant will be created here .       #
# partID: participant's anonymous identification number                                                         #
# mic: contains the audio recording from part two                                                               #
# mywin: the window created to display experimental visuals                                                     #
# noCue: the main experiment visual, with no cue                                                                #
# listen: the main experimental visual, with a cue to listen                                                    #
# record: the main experimanetal visual, with a cue to record                                                   #
#                                                                                                               #
# variables within functions are defined in the function                                                        #
#                                                                                                               #
# ###############################################################################################################

'''General setup'''

test = None
stories = {}
sentences = {}
segments = {}
wms = {}
path = os.path.abspath("") # gets pathway to folder with the .py file
partID = None
microphone.switchOn(sampleRate = 48000, outputDevice = None, bufferSize = None) # turns on the mic
mic = microphone.AdvAudioCapture(filename = "blah.wav")

# creation of visual cues outside of the functions to prevent re-creation every experimental loop
mywin = None
initialCue = None
noCue = None
listen = None
record = None

'''Defining all of the component functions'''

# Prompts the experimenter to enter the participant ID
def getParticipantInfo():
    global partID
    
    myDlg = gui.Dlg(title="Situational Coherence")
    myDlg.addText("Participant Info")
    myDlg.addField("Participant ID:")
    myDlg.show()  # shows dialog and waits for OK or cancel
    if myDlg.OK:  # decides to continue or cancel based on user command
        partID = myDlg.data #stores the participants ID#
    else:
        print 'experiment was cancelled'
        sys.exit()

# Prompts the user to select audio files and preloads them, creates folders for recordings and logging info
def setup():
    global partID
    global path
    global test
    
    # creates the folder for the log file and recordings in the folder containing the .py file
    if not os.path.exists(path + "/Participants/" + partID[0] + "/Recordings"):
        os.makedirs(path + "/Participants/" + partID[0] + "/Recordings") # creates the participant's folder and the recordings folder 
    logging.info("Participant folder " + str(partID) + " created")
    centralLog = logging.LogFile(path + "/Participants/" + partID[0] + "/" + partID[0] + ".log", level= 0) # creates the logging file
    
    # pre-loads the test stimulus
    root = Tkinter.Tk()
    root.withdraw()
    dirpath = tkFileDialog.askdirectory(parent = root, initialdir = path, title = "Please select a folder containing the test stimulus")
    os.chdir(dirpath) # changes the directory to the selected folder
    logging.info("Preloading test stimulus...")
    for audio in os.listdir(dirpath): # needed because Macs hide files that store custom attributes.
        if ".wav" in audio:
            logging.exp(audio + " was uploaded")
            test = sound.SoundPyo(value = audio) # creates a sound object from the sound file
    print test

    # pre-loads the stories for part one
    root = Tkinter.Tk()
    root.withdraw()
    dirpath = tkFileDialog.askdirectory(parent = root, initialdir = path, title = "Please select a folder containing the stories")
    os.chdir(dirpath) # changes the directory to the selected folder
    logging.info("Preloading stories...")
    for audio in os.listdir(dirpath):
        if ".wav" in audio:
            logging.exp(audio + " was uploaded")
            clip = sound.SoundPyo(value = audio)
            stories[audio] = clip # stores the created sound object in a dictionary
    print stories
    
    logging.flush() # flushes the logs up to this point, loggin info not saved in log file until log is flushed
    
    # pre-loads the sentences for part two
    root = Tkinter.Tk()
    root.withdraw()
    dirpath = tkFileDialog.askdirectory(parent = root, initialdir = path, title = "Please select a folder containing the sentences")
    os.chdir(dirpath)
    logging.info("Preloading sentences...")
    for audio in os.listdir(dirpath):
        if ".wav" in audio:
            logging.exp(audio + " was uploaded")
            sentence = sound.SoundPyo(value = audio)
            sentences[audio] = sentence
    print sentences
    
    logging.flush()
    
    # pre-loads the segments for part three
    root = Tkinter.Tk()
    root.withdraw()
    dirpath = tkFileDialog.askdirectory(parent = root, initialdir = path, title = "Please select a folder containing the segments")
    os.chdir(dirpath)
    logging.info("Preloading segments...")
    for audio in os.listdir(dirpath):
        if ".wav" in audio:
            logging.exp(audio + " was uploaded")
            segment = sound.SoundPyo(value = audio)
            segments[audio] = segment
    print segments
    
    logging.flush()
    
    # pre-loads the WMS paragraph for part four
    root = Tkinter.Tk()
    root.withdraw()
    dirpath = tkFileDialog.askdirectory(parent = root, initialdir = path, title = "Please select a folder containing the WMS paragraph")
    os.chdir(dirpath)
    logging.info("Preloading WMS...")
    for audio in os.listdir(dirpath):
        if ".wav" in audio:
            logging.exp(audio + " was uploaded")
            wmsSound = sound.SoundPyo(value = audio)
            wms[audio] = wmsSound
    print wms
    
    logging.flush()

# Selects the .csv files from which to read the story segments for part one
def readStoryCSV():
    clipOrder = [] # list storing the order of the story clips
    root = Tkinter.Tk()
    root.withdraw()
    blocks = tkFileDialog.askdirectory(parent = root, initialdir = path, title = "Please select a folder containing the stories (.csv files)")
    for block in os.listdir(blocks):
        if ".csv" in block:
            openFile = csv.reader(open(blocks + "/" + block, 'rU')) # opens the .csv file as a read only
            for row in openFile:
                if len(row[0]) > 2: # ignores the column heading, heading must be >2 characters
                   continue
                else:
                    #This may need to be changed later if audio files are renamed.
                    audio = row[0] + ".wav"
                    clipOrder.insert(len(clipOrder), audio) # fills clipOrder with the values in the .csv file
    print(clipOrder)
    return clipOrder
    
    logging.flush()
    
# selects the .csv file from which to read the sentence names for part two
def readSentenceCSV():
    sentOrder = [] # list storing the order of the sentences within a block
    sentBlocks = 0 # number of blocks (i.e. .csv files)
    sentPerBlock = 0 # number of sentneces per block
    root = Tkinter.Tk()
    root.withdraw()
    blocks = tkFileDialog.askdirectory(parent = root, initialdir = path, title = "Please select a folder containing the sentence blocks (.csv files)")
    for block in os.listdir(blocks):
        if ".csv" in block:
            sentBlocks += 1
            openFile = csv.reader(open(blocks + "/" + block, 'rU'))
            rowOrder = [] # list of rows in the .csv file, each represents a sentence
            for row in openFile:
                rowOrder.insert(len(rowOrder), row)
            random.shuffle(rowOrder) # randomly orders the values in rowOrder
            for row in rowOrder:
                if len(row[0]) > 2:
                   continue
                else:
                    sentPerBlock += 1
                    #This may need to be changed later if stimuli audio files are renamed.
                    audioOne = row[0] + row[1] + "_norm.wav" # stores the filename of the first sentence in the pair
                    audioTwo = row[0] + row[2] + "_norm.wav" # stores the filename of the second sentence in the pair
                    sentOrder.insert(len(sentOrder), audioOne)
                    sentOrder.insert(len(sentOrder), audioTwo) # fills sentOrder with the values in the .csv file in the appropriate order
    print(sentOrder)
    return sentOrder, sentPerBlock/sentBlocks, sentBlocks
    
    logging.flush()

# selects the .csv file from which to read the segments for part three
def readSegmentCSV():
    segOrder = [] # list storing the order of the segments
    root = Tkinter.Tk()
    root.withdraw()
    blocks = tkFileDialog.askdirectory(parent = root, initialdir = path, title = "Please select a folder containing the segment blocks (.csv files)")
    for block in os.listdir(blocks):
        if ".csv" in block:
            openFile = csv.reader(open(blocks + "/" + block, 'rU'))
            rowOrder = []
            for row in openFile:
                rowOrder.insert(len(rowOrder), row)
            random.shuffle(rowOrder)
            for row in rowOrder:
                if len(row[0]) > 2:
                   continue
                else:
                    #This may need to be changed later if stimuli audio files are renamed.
                    audio = row[0] + "_norm.wav"
                    segOrder.insert(len(segOrder), audio) # fills segOrder with the values in the .csv file
    print(segOrder)
    return segOrder
    
    logging.flush()
            
# Opens a window for experimenter to confirm initiation of the experiment
def initiateExperiment():
    myDlg = gui.Dlg(title="Situational Coherence")
    myDlg.addText("Experiment Ready")
    myDlg.addText("Press OK to start or Cancel to quit")
    myDlg.show()  # show dialog and wait for OK or Cancel
    if myDlg.OK:  # decides to continue or cancel based on user command
        choice = myDlg.data # stores the experimenter's choice to initiate the experiment
    else: # flushes the logs and stops running the code if the experiment is cancelled
        print "Goodbye!"
        logging.info("Experiment was cancelled")
        logging.flush()
        sys.exit() 

# Defines a window to display expertimental visuals, instructions and visual cues
def setWindow():
    global mywin
    global initialCue
    global noCue
    global listen
    global recall

   # defines the cue windows
    mywin = visual.Window([800,600], monitor = "testMonitor", units="deg")
    initialCue = visual.ImageStim(win = mywin, image = path + "/Cues/InitialCue.jpg", units = "deg", pos = (0.0,0.0), 
                               name = "initialCue", autoLog = True)
    noCue = visual.ImageStim(win = mywin, image = path + "/Cues/NoCue.jpg", units = "deg", pos = (0.0,0.0), 
                               name = "noCue", autoLog = True)
    listen = visual.ImageStim(win = mywin, image = path + "/Cues/Listen.jpg", units ="deg", pos = (0.0,0.0), 
                               name = "listen", autoLog = True)
    recall = visual.ImageStim(win = mywin, image = path + "/Cues/Recall.jpg", units = "deg", pos = (0.0,0.0), 
                               name = "recall", autoLog = True)

# Inserts a delay before checking the time, so as to not continuously check
def waitUntil(sec, internalTime):
    while internalTime.getTime() < sec:
        time.sleep(0.001)

# Runs a trial listening-recording loop
def trialRun():
    global initialCue
    global noCue
    global listen
    global recall
    global test
    
    # defines general instruction window
    generalInstruction = visual.ImageStim(win = mywin, image = path + "/Cues/General_Instructions.jpg", pos = (0.0, 0.0),
                                          name = "General_Instructions", autoLog = True)
    InitialCueInstruction = visual.ImageStim(win = mywin, image = path + "/Cues/InitialCue_Instructions.jpg", pos = (0.0, 0.0),
                                          name = "initialCue_Instructions", autoLog = True)
    ListenInstruction = visual.ImageStim(win = mywin, image = path + "/Cues/Listen_Instructions.jpg", pos = (0.0, 0.0),
                                          name = "Listen_Instructions", autoLog = True)
    RecallInstruction = visual.ImageStim(win = mywin, image = path + "/Cues/Recall_Instructions.jpg", pos = (0.0, 0.0),
                                          name = "Recall_Instructions", autoLog = True)
    endTestMessage = visual.TextStim(mywin, text = "Well done! Press the right arrow key when you are ready to begin section one.", units = "deg")
                                         
    # displays the instructions and runs the trial
    generalInstruction.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"): # waits for user key-press to continue
        key = event.waitKeys()
    InitialCueInstruction.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    ListenInstruction.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    RecallInstruction.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    initialCue.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    internalTime = core.Clock()
    internalTime.reset()
    test.play()
    logging.exp("playing test stimulus")
    print ("playing test stimulus")
    logging.exp("displaying listen cue")
    listen.draw()
    mywin.flip()
    waitUntil(4, internalTime) # waits to keep audio aligned with experiment
    logging.exp("end of test stimulus")
    noCue.draw()
    mywin.flip()
    waitUntil(5, internalTime) # waits 1 second before changing the cue (no recording is done for the test stimulus)
    logging.exp("displaying recall cue")
    recall.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    mic.stop(log = True) # stops recording once the user has pressed the right arrow key
    logging.exp("finished the test loop")
    logging.flush()
        
    # displays message indicating the first story is over
    endTestMessage.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()

# Segments of the stories are played in order, along with the appropriate visual cues
def storyLoop(stories):
    global mywin
    global initialCue
    global noCue
    global listen
    global recall
    
    # defines and displays the instruction windows
    storyInstruction = visual.ImageStim(win = mywin, image = path + "/Cues/Story_Instructions_1.jpg", pos = (0.0, 0.0),
                                          name = "Story_Instructions_1", autoLog = True)
    storyInstruction2 = visual.ImageStim(win = mywin, image = path + "/Cues/Story_Instructions_2.jpg", pos = (0.0, 0.0),
                                          name = "Story_Instructions_2", autoLog = True)
    endStoryMessage = visual.TextStim(mywin, text = "1/2 stories completed. Press the right arrow key to continue.", units = "deg")
    endStoriesMessage = visual.TextStim(mywin, text = "Thank you! Stories completed.", wrapWidth = 50, units = "deg")
    continueMessage = visual.TextStim(mywin, text = "Take a break! Press the right arrow key when you are ready to continue.")
    
    # displays the first experimental window
    storyInstruction.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    storyInstruction2.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()

    # plays the clips and records summaries for the first story
    stimCount = 1 # keeps track of how many clips have been played
    for clips in range(0, 8):
        duration = stories[str(stimCount) + ".wav"].getDuration() # gets the duration of the clip
        initialCue.draw()
        mywin.flip()
        key = event.waitKeys()
        while (key[0] != "right"):
            key = event.waitKeys()
        internalTime = core.Clock()
        internalTime.reset() # re-sets the internal time to keep track of timing for each clip
        stories[str(stimCount) + ".wav"].play() # plays the audio file stored under the key corresponding to the stimCount value
        logging.exp("playing story 1, clip " + str(stimCount))
        print ("playing story 1, clip " + str(stimCount))
        logging.exp("displaying listen cue")
        listen.draw()
        mywin.flip()
        waitUntil(duration, internalTime) # waits to keep audio aligned with experiment
        logging.exp("end of story 1, clip " + str(stimCount))
        noCue.draw()
        mywin.flip()
        waitUntil(duration + 1, internalTime) # waits 1 second before recording
        logging.exp("recording for story 1, clip " + str(stimCount))
        mic.record(sec = float("inf"), filename = "story1_clip" + str(stimCount) + "_recall" + ".wav", 
                   block = False) # begins recording
        logging.exp("displaying recall cue")
        recall.draw()
        mywin.flip()
        key = event.waitKeys()
        while (key[0] != "right"):
            key = event.waitKeys()
        mic.stop(log = True) # stops recording once the user has pressed the right arrow key
        logging.exp("finished recording for story 1, clip " + str(stimCount))
        stimCount += 1
        logging.flush()
        
    # displays message indicating the first story is over
    endStoryMessage.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
        
    # plays clips and records summaries for the second story
    for clips in range(9, 14):
        duration = stories[str(stimCount) + ".wav"].getDuration()
        initialCue.draw()
        mywin.flip()
        key = event.waitKeys()
        while (key[0] != "right"):
            key = event.waitKeys()
        internalTime = core.Clock()
        internalTime.reset()
        stories[str(stimCount) + ".wav"].play()
        logging.exp("playing story 2, clip " + str(stimCount))
        print ("playing story 2, clip " + str(stimCount))
        logging.exp("displaying listen cue")
        listen.draw()
        mywin.flip()
        waitUntil(duration, internalTime)
        logging.exp("end of story 2, clip " + str(stimCount))
        noCue.draw()
        mywin.flip()
        waitUntil(duration + 1, internalTime)
        logging.exp("recording for story 2, clip " + str(stimCount))
        mic.record(float("inf"), filename = "story2_clip" + str(stimCount) + "_recall" + ".wav", 
                   block = False)
        logging.exp("displaying recall cue")
        recall.draw()    
        mywin.flip()
        key = event.waitKeys()
        while (key[0] != "right"):
            key = event.waitKeys()
        mic.stop(log = True)
        logging.exp("finished recording for story 2, clip " + str(stimCount))
        stimCount += 1
        logging.flush()
    
    # displays message indicating that part one is done
    endStoriesMessage.draw()
    mywin.flip()
    internalTime = core.Clock()
    internalTime.reset()
    waitUntil(5, internalTime)
    continueMessage.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    
# Plays the audio for a single sentence pair while displaying the appropriate cues
def playSentences(audioOne, audioTwo):
    global mywin
    global initialCue
    global noCue
    global listen
    global recall
    
    initialCue.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    internalTime = core.Clock()
    internalTime.reset()
    sentences[audioOne].play() # plays the auio file
    logging.exp("playing audio file " + audioOne)
    print ("playing audio file " + audioOne)
    logging.exp("displaying listen cue")
    listen.draw()
    mywin.flip()
    waitUntil(4, internalTime) # keeps audio aligned with experiment
    logging.exp("end of " + audioOne)
    waitUntil(5, internalTime) # waits one second in between sentences
    sentences[audioTwo].play()
    logging.exp("playing audio file " + audioTwo)
    print ("playing audio file " + audioTwo)
    waitUntil(9, internalTime) # keeps audio aligned with experiment
    logging.exp("end of " + audioTwo)
    noCue.draw()
    mywin.flip()
    waitUntil(10, internalTime) # waits one second before recording
    logging.exp("recording for " + audioOne + " " + audioTwo + " pair")
    mic.record(float("inf"), filename = "Sentence_" + audioOne + "_" + audioTwo + "_recall" + ".wav", block = False)
    logging.exp("displaying recall cue")
    recall.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    mic.stop(log = True)
    logging.exp("end of recording for " + audioOne + " " + audioTwo + " pair")

# plays all of the sentences pairs, records the participant, & displays the appropriate cues
def sentenceLoop(sentences, sentPerBlock, sentBlocks):
    # defines the instruction windows
    sentenceInstruction = visual.ImageStim(win = mywin, image = path + "/Cues/Sentence_Instructions.jpg", pos = (0.0, 0.0),
                                          name = "Sentence_Instructions", autoLog = True)
    blockDoneMessage = visual.TextStim(mywin, text = "1/2 sentence blocks done. Press the right arrow key to continue.")
    endSentencesMessage = visual.TextStim(mywin, text = "Thank you! Sentence blocks completed.", wrapWidth = 50, units = "deg")
    continueMessage = visual.TextStim(mywin, text = "Take a break! Press the right arrow key when you are ready to continue.")
    
    sentenceInstruction.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    mywin.clearBuffer()
    
    # the sentence loop
    audioPair = 0 # keep track of where you are in the list of stimuli
    stimCount = 0 # keeps track how many stimuli have been completed
    blocksDone = 0 # keeps track how many blocks have been completed
    for audio in range(0, len(sentences)/2):
        logging.flush()
        # will need to modify in the future if stimuli per block changes in the future.
        if stimCount % 12 == 0:
            if (blocksDone > 0):
                blockDoneMessage.draw()
                mywin.flip()
                print ("Block " + str(blocksDone) + " completed. waiting for user command to start next block.")
            blocksDone += 1
        stimCount += 1
        print "stimulus " + str(stimCount % 12) # prints how many stimuli have been run in a block
        playSentences(sentences[audioPair], sentences[audioPair + 1]) # plays the loaded sentence pair
        audioPair += 2
        logging.flush()
    
    # displays message indicating that the sentences are over.
    endSentencesMessage.draw()
    mywin.flip()
    internalTime = core.Clock()
    internalTime.reset()
    waitUntil(5, internalTime)
    continueMessage.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    
# Plays the segments, records the participant's recall, & diplays the appropriate visual cues
def segmentLoop(segOrder, segments):
    global initialCue
    global noCue
    global listen
    global recall

    # defines the instruction windows
    segmentInstruction = visual.ImageStim(win = mywin, image = path + "/Cues/Segment_Instructions_1.jpg", pos = (0.0, 0.0),
                                          name = "Segment_Instructions_1", autoLog = True)
    segmentInstruction2 = visual.ImageStim(win = mywin, image = path + "/Cues/Segment_Instructions_2.jpg", pos = (0.0, 0.0),
                                          name = "Segment_Instructions_2", autoLog = True)
    endSegmentsMessage = visual.TextStim(mywin, text = "Thank you. Segments completed.", wrapWidth = 50, units = "deg")
    continueMessage = visual.TextStim(mywin, text = "Take a break! Press the right arrow key when you are ready to continue.")
    
    segmentInstruction.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    segmentInstruction2.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    for audio in segOrder:
        duration = segments[audio].getDuration()
        initialCue.draw()
        mywin.flip()
        key = event.waitKeys()
        while (key[0] != "right"):
            key = event.waitKeys()
        internalTime = core.Clock()
        internalTime.reset()
        segments[audio].play()
        logging.exp("playing audio file " + audio)
        print ("playing audio file " + audio)
        logging.exp("displaying listen cue")
        listen.draw()
        mywin.flip()
        waitUntil(duration, internalTime)
        logging.exp("end of segment" + audio)
        noCue.draw()
        mywin.flip()
        waitUntil(duration + 1, internalTime)
        logging.exp("recording for segment" + audio)
        mic.record(float("inf"), filename = "Segment_" + audio + "_recall" + ".wav", 
                   block = False)
        logging.exp("displaying recall cue")
        recall.draw()    
        mywin.flip()
        key = event.waitKeys()
        while (key[0] != "right"):
            key = event.waitKeys()
        mic.stop(log = True)
        logging.exp("finished recording for segment " + audio)
        logging.flush()
    
    # displays message indicating that the segments are over.
    endSegmentsMessage.draw()
    mywin.flip()
    internalTime = core.Clock()
    internalTime.reset()
    waitUntil(5, internalTime)
    continueMessage.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    
# Plays the WMS paragraph and records the participant's recall
def playWMS():
    global initialCue
    global noCue
    global listen
    global recall
    
    wmsInstruction = visual.ImageStim(win = mywin, image = path + "/Cues/WMS_Instructions.jpg", pos = (0.0, 0.0),
                                          name = "WMS_Instructions", autoLog = True)
    endExperimentMessage = visual.TextStim(mywin, text = "Thank you! Experiment completed.", wrapWidth = 50, units = "deg")
    
    wmsInstruction.draw()
    mywin.flip()
    key = event.waitKeys()
    while (key[0] != "right"):
        key = event.waitKeys()
    wmsCount = 0
    for audio in wms:
    # duration = wms["wms_norm.wav"].getDuration()
        duration = wms[audio].getDuration()
        initialCue.draw()
        mywin.flip()
        key = event.waitKeys()
        while (key[0] != "right"):
            key = event.waitKeys()
        internalTime = core.Clock()
        internalTime.reset()
        wms[audio].play()
        logging.exp("playing wms " + str(wmsCount))
        print ("playing wms " + str(wmsCount))
        logging.exp("displaying listen cue")
        listen.draw()
        mywin.flip()
        waitUntil(duration, internalTime)
        logging.exp("end of wms " + str(wmsCount))
        noCue.draw()
        mywin.flip()
        waitUntil(duration + 1, internalTime)
        logging.exp("recording for wms " + str(wmsCount))
        mic.record(float('inf'), filename = "WMS_" + str(wmsCount) + "_recall.wav", 
                    block = False)
        logging.exp("displaying recall cue")
        recall.draw()    
        mywin.flip()
        key = event.waitKeys()
        while (key[0] != "right"):
            key = event.waitKeys()
        mic.stop(log=True)
        logging.exp("finished recording for wms " + str(wmsCount))
        wmsCount += 1
        logging.flush()
    
    # displays message indicating that the experiment over.
    endExperimentMessage.draw()
    mywin.flip()
    internalTime = core.Clock()
    internalTime.reset()
    waitUntil(10, internalTime)

# Executes all the component functions in the proper order
def main():
    # setup
    getParticipantInfo()
    setup()
    clipOrder = readStoryCSV()
    sentOrder, sentPerBlock, sentBlocks = readSentenceCSV()
    segOrder = readSegmentCSV()
    os.chdir(path + "/Participants/" + partID[0] + "/Recordings")
    initiateExperiment()
    setWindow()
    
    trialRun() # trial run
    storyLoop(stories) # part one
    sentenceLoop(sentOrder, sentPerBlock, sentBlocks) # part two
    segmentLoop(segOrder, segments) # part three
    playWMS() # part four
    
    # logging and exit
    logging.info("Sentences presented in the following order: " + str(sentOrder))
    logging.info("Segments presented in the following order: " + str(segOrder))
    time.sleep(10)    
    logging.flush() 
    sys.exit()

# lets python know which function is the main function
if __name__ == "__main__":
    main ()