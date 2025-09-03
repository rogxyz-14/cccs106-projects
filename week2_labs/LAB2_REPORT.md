# Lab 2 Report: Git Version Control and Flet GUI Development

**Student Name:** Roger A. Regalado Jr.\
**Student ID:** 231005317\
**Section:** BSCS 3B\
**Date:** September 4, 2025

## Git Configuration

### Repository Setup
- **GitHub Repository:** [Your repository URL]
- **Local Repository:** ✅ Initialized and connected
- **Commit History:** [Number] commits with descriptive messages

### Git Skills Demonstrated
- ✅ Repository initialization and configuration
- ✅ Adding, committing, and pushing changes
- ✅ Branch creation and merging
- ✅ Remote repository management

## Flet GUI Applications

### 1. hello_flet.py
- **Status:** ✅ Completed
- **Features:** Interactive greeting, student info display, dialog boxes
- **UI Components:** Text, TextField, Buttons, Dialog, Containers
- **Notes:** It was challenging to learn the Flet component structure, and how the events (such as clicking on a button) refresh the UI. At first, the greeting message did not show up until I applied the page. update () function because this was the one that demonstrated to me how Flet can update the interface. I also had no other option but to revise the render of container and rows to achieve a more organized interface.

### 2. personal_info_gui.py
- **Status:** ✅ Completed
- **Features:** Form inputs, dropdowns, radio buttons, profile generation
- **UI Components:** TextField, Dropdown, RadioGroup, Containers, Scrolling
- **Error Handling:** Input validation and user feedback
- **Notes:** The major problem was the input validation and this was primarily at the point of users typing invalid data, or where they were typing incomplete data. This was fixed by adding error management (try/except) and crashing on entry to the non-numeric values as age. The other issue was to co-ordinate various elements (text fields, dropdowns, radio buttons etc) and ensure that the elements and materials in the page were in their respective positions, which helped me to improve my understanding on how the layout is handled in Flet.

## Technical Skills Developed

### Git Version Control
- Understanding of repository concepts
- Basic Git workflow (add, commit, push)
- Branch management and merging
- Remote repository collaboration

### Flet GUI Development
- Flet 0.28.3 syntax and components
- Page configuration and layout management
- Event handling and user interaction
- Modern UI design principles

## Challenges and Solutions

One difficulty was dealing with Git setup and linking the local repository with GitHub. At first, push commands failed because my name was not set to main and my remote URL checked. In Flet the slowest task was debugging missing dependencies and layout alignment bugs. These problems were resolved with installing the right version (flet==0.28.3) and testing different columns, rows and containers. In general, the remedial steps were to meticulously adhere to documentation and test out the code step after step.

## Learning Outcomes

This lab gave me an opportunity to learn the basics of version control using Git such as creating repositories, making commits, branching, and pushing to GitHub. Other essential practical skills I found in Flet were working with interactive GUI applications and event-handling and layout concepts. More importantly, I realized just how much version control and GUI development are part of the collaborative programming model that allows it easier to track innovations, control features, and jointly share their work.

## Screenshots

### Git Repository
- [ ] GitHub repository with commit history
- [ ] Local git log showing commits

### GUI Applications
- [ ] hello_flet.py running with all features
- [ ] personal_info_gui.py with filled form and generated profile

## Future Enhancements

In order to improve on the same in the future, I would consider having better designs on the GUIs in terms of style, themes, and looking modern with an improved number of icons. I might add an option such as saving the profile information when creating personal information user interface as a file (csv or json file) or show uploaded profile picture in the user interface personal information gui.py. I will also understand more higher-level Git, such as how to use pull requests to collaborate with other people and tags to monitor versions.