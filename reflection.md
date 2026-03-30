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

- What constraints does your scheduler consider (for example: time, priority, preferences)? How did you decide which constraints mattered most?

The scheduler considers available time and task priority. Critical tasks always go in the plan first because missing a medication or vet visit causes real harm.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes. Why is that tradeoff reasonable for this scenario?

One tradeoff is for performance where the sorting algorithm terminates early. The tradeoff was reasonable since entries are sorted by dates, allowing early inner loop termination.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)? What kinds of prompts or questions were most helpful?

Claude Code was used to implement and improve scheduling methods like conflict detection and task filtering. Asking for a list of small improvements first was useful because it gave clear options to pick from.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is. How did you evaluate or verify what the AI suggested?

The AI suggested three algorithm options for conflict detection and the best one was chosen. The tests were run after each change to check that the output was still correct.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test? Why were these tests important?

The tests checked sorting order, recurring task creation, and conflict detection. These tests matter because a wrong plan or missed conflict could mean a pet skips a meal or a medication.

**b. Confidence**

- How confident are you that your scheduler works correctly? What edge cases would you test next if you had more time?

The scheduler is confident for single-day use with a small number of tasks. With more time the next tests would cover tasks that span midnight and monthly recurrence across different month lengths.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The conflict detection is the most satisfying part because it is useful and the early-exit sort makes it efficient. It also shows clearly how data structures and algorithms connect to a real problem.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The monthly recurrence would use a real calendar library instead of a 30-day guess. The daily plan would also warn the user when critical tasks alone go over the time budget.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Breaking a big system into small classes with clear jobs makes it easy to add new features later. AI is most helpful when you ask it for options first and then pick the one that fits best.
