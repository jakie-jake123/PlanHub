

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(250) NOT NULL UNIQUE,
    password VARCHAR(250) NOT NULL
);




CREATE TABLE termins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,

    title VARCHAR(200) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,

    is_exam BOOLEAN DEFAULT FALSE,
    mute_mode BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);


"""
CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content VARCHAR(100),
    due DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""