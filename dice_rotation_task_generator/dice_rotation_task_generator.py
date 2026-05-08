import random
import die

# File to write the generated tasks to
OUTPUT_FILE = "./SpatialReasoning_Benchtools/tasks/final_3d_complex_rotate_die/values.csv"
SPR_OUTPUT_FILE = "./src/spatialreasoning/tasks/final_3d_complex_rotate_die/values.csv"

# Number of each task with each number of steps to generate
NUM_TASKS = 30

# Minimum and maximum number of steps in a task
MIN_STEPS = 1
MAX_STEPS = 5

# Die face options
FACES = ['front', 'back', 'top', 'bottom', 'left', 'right']

# Rotation degree options
DEGREES = [-90, -180, -270, 90, 180, 270]

# Rotation direction options
DIRECTIONS = ['clockwise', 'counterclockwise']


# Function to generate a random die rotation task of random number of steps (between 1 and n)
def generate_task(num_steps):
    # Create a new random die
    d = die.Die()

    # Get initial state of the die
    initial_die_state = str(d)

    # Generate the steps for the task
    steps = []
    for _ in range(num_steps):
        face = random.choice(FACES)
        degrees = random.choice(DEGREES)
        direction = random.choice(DIRECTIONS)
        steps.append((face, degrees, direction))

    for step in steps:
        d.rotate(step[0], step[1], step[2])
    
    solution = str(d)


    return initial_die_state, steps, solution, num_steps

# Generate and print the tasks (human readable format)
# for i in range(NUM_TASKS):
#     initial_state, steps, solution = generate_task()
#     print(f"Task {i+1}:")
#     print(f"Initial Die State: {initial_state}")
#     print("Steps:")
#     for step in steps:
#         print(f"  Rotate {step[0]} face {step[1]} degrees {step[2]}")
#     print(f"Final Die State: {solution}")
#     print("---------------------------------------------")

# Write the value file headers to the values file
with open(OUTPUT_FILE, "w") as output_file:
    output_file.write("starting_state,transformations,reference,number_of_steps\n")  # Write header

# Generate the tasks and write them to the values file
with open(OUTPUT_FILE, "a") as output_file:
    for num_steps in range(MIN_STEPS, MAX_STEPS + 1):
        for i in range(NUM_TASKS):
            initial_state, steps, solution, num_steps = generate_task(num_steps)
            steps_str = ", ".join([f"rotate {step[0]} face {step[1]} degrees {step[2]}" for step in steps])
            output_file.write(f"\"{initial_state}\",\"{steps_str}\",\"{solution}\",\"{num_steps}\"\n")



with open(SPR_OUTPUT_FILE, "w") as output_file:
    output_file.write("starting_state,transformations,correct_answer,number_of_steps\n")  # Write header

# Generate the tasks and write them to the values file
with open(SPR_OUTPUT_FILE, "a") as output_file:
    for num_steps in range(MIN_STEPS, MAX_STEPS + 1):
        for i in range(NUM_TASKS):
            initial_state, steps, solution, num_steps = generate_task(num_steps)
            steps_str = ", ".join([f"rotate {step[0]} face {step[1]} degrees {step[2]}" for step in steps])
            output_file.write(f"\"{initial_state}\",\"{steps_str}\",\"{solution}\",\"{num_steps}\"\n")


