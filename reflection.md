# PawPal+ Project Reflection

## 1. System Design

The three core actions that a User must be able to do:
    - managing their pets' profiles
    - managing the user's schedule restrictions
    - managing the user's recommended tasks for their pets

**a. Initial design**

- Briefly describe your initial UML design. What classes did you include, and what responsibilities did you assign to each?

The UML design consists of 4 main objects. The first is the User, which is contains the methods that allow users to view their schedule and add/ remove pets. Each user can have as many pets as they want so the next class is Pet, where each pet has a given schedule of tasks. Hence, each Pet "has" a Schedule, the third class that manages the routine and tasks of a pet. Finally, a Schedule "contains" at least one Task which is the last class that strictly define the type of task needed to perform. Each class has their own respective metadata associated with them.

**b. Design changes**

- Did your design change during implementation? If yes, describe at least one change and why you made it.
One change, the schedule would also have a reference to the Pet object. This would let schedule.pet.name to be easily accessible from the Schedule class.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
