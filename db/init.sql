DROP TABLE IF EXISTS game_questions CASCADE;
DROP TABLE IF EXISTS games CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    description VARCHAR(500),
    explanation VARCHAR(500),
    category VARCHAR(255) NOT NULL,
    difficulty VARCHAR(255) NOT NULL,
    answers jsonb NOT NULL,
    correct_answers jsonb NOT NULL
);

CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    rounds INTEGER NOT NULL,
    score INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS game_questions (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES games(id),
    question_id INTEGER NOT NULL REFERENCES questions(id),
    selected_answer_index INTEGER,
    is_correct BOOLEAN,
    answered_at TIMESTAMP,
    UNIQUE(game_id, question_id)
);


INSERT INTO users (username) VALUES
    ('Gabigol'),
    ('Arrascaeta'),
    ('Filipe_Luis'),
    ('Bruno_Henrique'),
    ('Gonzalo_Plata'),
    ('Wesley');

INSERT INTO questions (question, description, explanation, category, difficulty, answers, correct_answers) VALUES
    (
        'What is the capital of France?',
        'Choose the city that serves as the capital of France',
        'Paris has been the capital of France since 508 CE',
        'Geography',
        'easy',
        '["Paris", "London", "Berlin", "Madrid"]',
        '[true, false, false, false]'
    ),
    (
        'Which programming language was created by Guido van Rossum?',
        'Select the programming language developed by Guido van Rossum in 1991',
        'Python was created by Guido van Rossum and first released in 1991',
        'Programming',
        'medium',
        '["Java", "Python", "C++", "Ruby"]',
        '[false, true, false, false]'
    ),
    (
        'What is the largest planet in our solar system?',
        'Select the largest planet by size in the solar system',
        'Jupiter is the largest planet, with a mass more than twice that of all other planets combined',
        'Science',
        'easy',
        '["Mars", "Venus", "Jupiter", "Saturn"]',
        '[false, false, true, false]'
    ),
    (
        'Which data structure follows the LIFO principle?',
        'Choose the data structure that follows Last In, First Out principle',
        'Stack follows LIFO - the last element added is the first one to be removed',
        'Programming',
        'medium',
        '["Queue", "Stack", "Array", "Tree"]',
        '[false, true, false, false]'
    ),
    (
        'What is the chemical symbol for gold?',
        'Select the correct chemical symbol for the element gold',
        'Au comes from the Latin word for gold, "aurum"',
        'Science',
        'easy',
        '["Ag", "Au", "Fe", "Cu"]',
        '[false, true, false, false]'
    ),
    (
        'Which sorting algorithm has the best average time complexity?',
        'Select the sorting algorithm with O(n log n) average time complexity',
        'QuickSort has an average time complexity of O(n log n) and is generally considered the fastest sorting algorithm in practice',
        'Programming',
        'hard',
        '["Bubble Sort", "Quick Sort", "Insertion Sort", "Selection Sort"]',
        '[false, true, false, false]'
    );

INSERT INTO games (user_id, rounds, score, created_at) VALUES
    (1, 5, 4, '2024-01-01 10:00:00'),
    (1, 3, 2, '2024-01-02 11:30:00'),
    (2, 4, 3, '2024-01-03 14:15:00'),
    (3, 6, 5, '2024-01-04 16:45:00'),
    (4, 3, 3, '2024-01-05 09:20:00'),
    (5, 5, 4, '2024-01-06 13:10:00');

INSERT INTO game_questions (game_id, question_id, selected_answer_index, is_correct, answered_at) VALUES
    (1, 1, 0, true, '2024-01-01 10:01:00'),
    (1, 2, 1, true, '2024-01-01 10:02:00'),
    (1, 3, 2, true, '2024-01-01 10:03:00'),
    (1, 4, 1, true, '2024-01-01 10:04:00'),
    (1, 5, 0, false, '2024-01-01 10:05:00'),
    (2, 1, 0, true, '2024-01-02 11:31:00'),
    (2, 2, 2, false, '2024-01-02 11:32:00'),
    (2, 3, 2, true, '2024-01-02 11:33:00');