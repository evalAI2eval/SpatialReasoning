import random

# All pairs of opposite face values (1,6) (2,5) (3,4) 
FACE_NUMBERS = [[1,6],[2,5],[3,4]]

# Left face values, determined by the front and top face values, this cannot be randomized
left_face_value = {
    (1, 2): 3, (1, 3): 5, (1, 4): 2, (1, 5): 4,
    (2, 1): 4, (2, 3): 1, (2, 4): 6, (2, 6): 3,
    (3, 1): 2, (3, 2): 6, (3, 5): 1, (3, 6): 5,
    (4, 1): 5, (4, 2): 1, (4, 5): 6, (4, 6): 2,
    (5, 1): 3, (5, 3): 6, (5, 4): 1, (5, 6): 4,
    (6, 2): 4, (6, 3): 2, (6, 4): 5, (6, 5): 3
}

# Relative faces (used to simplify the rotation logic)
relative_faces = {
    'front': ['top', 'right', 'bottom', 'left'],
    'back': ['top', 'left', 'bottom', 'right'],
    'top': ['back', 'right', 'front', 'left'],
    'bottom': ['front', 'right', 'back', 'left'],
    'left': ['top', 'front', 'bottom', 'back'],
    'right': ['top', 'back', 'bottom', 'front']
}

# Text representation of a randomized die
class Die:
    # Initialize die with random face values
    def __init__(self):
        random.shuffle(FACE_NUMBERS)

        self.front = random.choice(FACE_NUMBERS[0])
        self.back = 7 - self.front
        self.top = random.choice(FACE_NUMBERS[1])
        self.bottom = 7 - self.top
        self.left = left_face_value[(self.front, self.top)] # Left face value is determined by the front and top face values
        self.right = 7 - self.left
            
    # String representation of the die
    def __str__(self):
        return f"Front: {self.front}, Back: {self.back}, Top: {self.top}, Bottom: {self.bottom}, Left: {self.left}, Right: {self.right}"

    # Rotate the die by a specified face, direction, and degrees
    def rotate(self, face, degrees, direction):
        # Validate the face
        if face not in ['front', 'back', 'top', 'bottom', 'left', 'right']:
            raise ValueError("Invalid face. Must be one of 'front', 'back', 'top', 'bottom', 'left', 'right'.")
        
        # Get the relative faces based on the face being rotated (as if face being rotated is the front face)
        rel_faces = relative_faces[face]
        relative_top, relative_right, relative_bottom, relative_left = rel_faces[0], rel_faces[1], rel_faces[2], rel_faces[3]

        # Validate the direction and degrees
        if direction not in ['clockwise', 'counterclockwise']:
            raise ValueError("Invalid direction. Must be 'clockwise' or 'counterclockwise'.")
        if degrees % 90 != 0:
            raise ValueError("Degrees must be a multiple of 90.")
        
        # Rotate the die clockwise
        if (direction == 'clockwise' and degrees >= 0) or (direction == 'counterclockwise' and degrees < 0):
            for _ in range(abs(degrees) // 90):
                relative_top_value = getattr(self, relative_top)
                relative_right_value = getattr(self, relative_right)
                relative_bottom_value = getattr(self, relative_bottom)
                relative_left_value = getattr(self, relative_left)
                setattr(self, relative_top, relative_left_value)
                setattr(self, relative_right, relative_top_value)
                setattr(self, relative_bottom, relative_right_value)
                setattr(self, relative_left, relative_bottom_value)

        # Rotate the die counterclockwise
        elif (direction == 'counterclockwise' and degrees >= 0) or (direction == 'clockwise' and degrees < 0):
            for _ in range(abs(degrees) // 90):
                relative_top_value = getattr(self, relative_top)
                relative_right_value = getattr(self, relative_right)
                relative_bottom_value = getattr(self, relative_bottom)
                relative_left_value = getattr(self, relative_left)
                setattr(self, relative_top, relative_right_value)
                setattr(self, relative_right, relative_bottom_value)
                setattr(self, relative_bottom, relative_left_value)
                setattr(self, relative_left, relative_top_value)

