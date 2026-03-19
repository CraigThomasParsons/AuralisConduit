use crossterm::{
    event::{self, Event as CEvent, KeyCode, KeyEventKind},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout},
    style::{Color, Style},
    text::{Line, Span},
    widgets::{Block, Borders, List, ListItem, ListState, Paragraph},
    Terminal,
};
use std::{
    env,
    error::Error,
    fs,
    io,
    path::PathBuf,
    time::Duration,
};
use tokio::sync::mpsc;
use tokio::time::sleep;
use uuid::Uuid;

enum Event {
    Input(CEvent),
    Tick,
    ResponseFound(String, String), // JobId, Response text
}

#[derive(Clone)]
enum Role {
    User,
    Auralis,
}

#[derive(Clone)]
struct Message {
    role: Role,
    content: String,
}

struct App {
    messages: Vec<Message>,
    input: String,
    active_job: Option<String>,
}

impl App {
    fn new() -> Self {
        Self {
            messages: vec![
                Message {
                    role: Role::Auralis,
                    content: "Welcome to Auralis Conduit CLI! Type your message to ChatGPT below.\nPress ESC to exit.".to_string(),
                }
            ],
            input: String::new(),
            active_job: None,
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    // Determine Auralis root path
    let mut current_dir = env::current_dir()?;
    let root_dir = if current_dir.ends_with("cli") {
        current_dir.pop();
        current_dir
    } else {
        current_dir
    };

    // Setup Terminal
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // Channel for events
    let (tx, mut rx) = mpsc::channel(100);

    // Dedicated input thread
    let tx_input = tx.clone();
    tokio::spawn(async move {
        loop {
            if event::poll(Duration::from_millis(50)).unwrap() {
                if let Ok(c_event) = event::read() {
                    tx_input.send(Event::Input(c_event)).await.unwrap();
                }
            } else {
                let _ = tx_input.send(Event::Tick).await;
            }
        }
    });

    let mut app = App::new();

    loop {
        terminal.draw(|f| {
            let chunks = Layout::default()
                .direction(Direction::Vertical)
                .margin(1)
                .constraints([
                    Constraint::Min(3),
                    Constraint::Length(3),
                ].as_ref())
                .split(f.size());

            let mut list_items = Vec::new();
            for msg in &app.messages {
                let role_style = match msg.role {
                    Role::User => Style::default().fg(Color::Cyan),
                    Role::Auralis => Style::default().fg(Color::Green),
                };
                let role_name = match msg.role {
                    Role::User => "[You]: ",
                    Role::Auralis => "[Auralis]: ",
                };
                
                // Handle newlines efficiently
                for (i, line) in msg.content.lines().enumerate() {
                    if i == 0 {
                        list_items.push(ListItem::new(Line::from(vec![
                            Span::styled(role_name, role_style),
                            Span::raw(line),
                        ])));
                    } else {
                        list_items.push(ListItem::new(Line::from(vec![
                            Span::raw(" ".repeat(role_name.len())),
                            Span::raw(line),
                        ])));
                    }
                }
                list_items.push(ListItem::new(Line::from("")));
            }
            
            if app.active_job.is_some() {
                list_items.push(ListItem::new(Line::from(vec![
                    Span::styled("[Auralis]: ", Style::default().fg(Color::Yellow)),
                    Span::raw("Generating (waiting for browser extension)..."),
                ])));
            }

            let messages_list = List::new(list_items.clone())
                .block(Block::default().borders(Borders::ALL).title(" Chat History "));
            
            // Auto scroll to bottom
            let mut state = ListState::default();
            state.select(Some(list_items.len().saturating_sub(1)));
            f.render_stateful_widget(messages_list, chunks[0], &mut state);

            let input_title = if app.active_job.is_some() { " Input (Locked) " } else { " Input " };
            let input_paragraph = Paragraph::new(app.input.as_str())
                .style(Style::default().fg(Color::Yellow))
                .block(Block::default().borders(Borders::ALL).title(input_title));
            f.render_widget(input_paragraph, chunks[1]);
        })?;

        if let Some(event) = rx.recv().await {
            match event {
                Event::Input(c_event) => {
                    if let CEvent::Key(key) = c_event {
                        if key.kind == KeyEventKind::Press {
                            match key.code {
                                KeyCode::Esc => break,
                                KeyCode::Char('c') if key.modifiers.contains(crossterm::event::KeyModifiers::CONTROL) => break,
                                KeyCode::Char(c) => {
                                    if app.active_job.is_none() {
                                        app.input.push(c);
                                    }
                                }
                                KeyCode::Backspace => {
                                    if app.active_job.is_none() {
                                        app.input.pop();
                                    }
                                }
                                KeyCode::Enter => {
                                    if !app.input.trim().is_empty() && app.active_job.is_none() {
                                        let prompt = app.input.clone();
                                        app.messages.push(Message {
                                            role: Role::User,
                                            content: prompt.clone(),
                                        });
                                        app.input.clear();

                                        let job_id = format!("job_{}", Uuid::new_v4().simple());
                                        app.active_job = Some(job_id.clone());

                                        let inbox_dir = root_dir.join("inbox").join(&job_id);
                                        let _ = fs::create_dir_all(&inbox_dir);
                                        
                                        let _ = fs::write(
                                            inbox_dir.join("briefing.md"),
                                            format!("===FILE: payload.md===\n{}", prompt),
                                        );
                                        
                                        // Target exact Auralis custom GPT
                                        let _ = fs::write(
                                            inbox_dir.join("url.txt"),
                                            "https://chatgpt.com/g/g-p-69b999011d348191951b6a69c247a2b2/c/69b9b6ec-e158-8332-864b-4b5ddea80bcc",
                                        );

                                        let tx_resp = tx.clone();
                                        let runs_dir = root_dir.join("runs").join(&job_id);
                                        let failed_dir = root_dir.join("failed").join(&job_id);
                                        
                                        tokio::spawn(async move {
                                            loop {
                                                sleep(Duration::from_secs(1)).await;
                                                let response_file = runs_dir.join("response.txt");
                                                if response_file.exists() {
                                                    if let Ok(content) = fs::read_to_string(&response_file) {
                                                        let _ = tx_resp.send(Event::ResponseFound(job_id, content)).await;
                                                        break;
                                                    }
                                                }
                                                if failed_dir.exists() {
                                                    let _ = tx_resp.send(Event::ResponseFound(job_id, "[SYSTEM MESSAGE] Job failed on the backend. Please check the browser.".to_string())).await;
                                                    break;
                                                }
                                            }
                                        });
                                    }
                                }
                                _ => {}
                            }
                        }
                    }
                }
                Event::ResponseFound(job_id, response) => {
                    if Some(job_id) == app.active_job {
                        app.messages.push(Message {
                            role: Role::Auralis,
                            content: response,
                        });
                        app.active_job = None;
                    }
                }
                Event::Tick => {}
            }
        }
    }

    // Cleanup Terminal
    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;

    Ok(())
}
