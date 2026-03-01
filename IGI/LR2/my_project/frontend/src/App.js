import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API = 'http://localhost:8000/api/todos/';

function App() {
  const [todos, setTodos]   = useState([]);
  const [title, setTitle]   = useState('');
  const [loading, setLoading] = useState(true);

  const fetchTodos = async () => {
    const res = await axios.get(API);
    setTodos(res.data);
    setLoading(false);
  };

  useEffect(() => { fetchTodos(); }, []);

  const addTodo = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    await axios.post(API, { title, completed: false });
    setTitle('');
    fetchTodos();
  };

  const toggleTodo = async (todo) => {
    await axios.patch(`${API}${todo.id}/`, { completed: !todo.completed });
    fetchTodos();
  };

  const deleteTodo = async (id) => {
    await axios.delete(`${API}${id}/`);
    fetchTodos();
  };

  return (
    <div className="app">
      <h1>📝 Todo App</h1>
      <p className="subtitle">React + Django + SQLite + Docker</p>

      <form onSubmit={addTodo} className="form">
        <input
          value={title}
          onChange={e => setTitle(e.target.value)}
          placeholder="Новая задача..."
        />
        <button type="submit">Добавить</button>
      </form>

      {loading ? (
        <p className="loading">Загрузка...</p>
      ) : (
        <ul className="todo-list">
          {todos.length === 0 && <p className="empty">Задач пока нет 🎉</p>}
          {todos.map(todo => (
            <li key={todo.id} className={`todo-item ${todo.completed ? 'done' : ''}`}>
              <span onClick={() => toggleTodo(todo)} className="todo-title">
                {todo.completed ? '✅' : '⬜'} {todo.title}
              </span>
              <button onClick={() => deleteTodo(todo.id)} className="delete-btn">🗑️</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
