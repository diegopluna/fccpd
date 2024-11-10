CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    question VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    explanation VARCHAR(255),
    category VARCHAR(255) NOT NULL,
    difficulty VARCHAR(255) NOT NULL,
    answers jsonb NOT NULL,
    correct_answers jsonb NOT NULL
);

-- Create games table
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
