#include <gtk/gtk.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <math.h>

/*=====================*/
/*   Game Parameters   */
/*=====================*/
#define LED_MATRIX_WIDTH  20    // 20 columns (each column is one strip)
#define LED_MATRIX_HEIGHT 40    // 40 rows (pixels per strip)
#define BLOCK_SIZE        2     // each snake unit and apple covers 2x2 LED pixels
#define SCALE 20                // scaling factor for drawing
#define MAX_SNAKE 1000

static int frames_per_second = 5;         // default fps (adjustable via '+'/'-' keys)
static int timer_interval_ms = 1000 / 5;    // computed from fps

typedef struct {
    int x, y;  // LED coordinates (0-indexed)
} Point;

/* Global game state */
static Point snake[MAX_SNAKE];  // snake[0] is the head
static int snake_length = 3;
static int dx = BLOCK_SIZE;     // initial velocity: rightward (in pixels per frame)
static int dy = 0;
static Point apple;
static bool game_over = false;
static GtkWidget *drawing_area = NULL;

/*===========================*/
/* UDP Sending Configuration */
/*===========================*/
#define NUM_DEVICES 5
#define STRIPS_PER_DEVICE 4
#define PIXELS_PER_STRIP 40
#define MAX_MESSAGE_LEN 2048

struct ESPConfig {
    const char* ip;
    int port;
    int first_strip_number;  // starting global strip number (1-indexed)
};

// static const struct ESPConfig ESP_DEVICES[NUM_DEVICES] = {
//     {"172.20.10.14", 12341, 1},
//     {"172.20.10.2",  12342, 5},
//     {"172.20.10.8",  12343, 9},
//     {"172.20.10.5",  12344, 13},
//     {"172.20.10.6",  12345, 17}
// };
static const struct ESPConfig ESP_DEVICES[NUM_DEVICES] = {
    {"192.168.18.49", 12341, 1},
    {"192.168.18.115",  12342, 5},
    {"192.168.18.53",  12343, 9},
    {"192.168.18.54",  12344, 13},
    {"192.168.18.109",  12345, 17}
};



struct ESPConnection {
    int socket;
    struct sockaddr_in address;
};

struct ESPConnection* esp_connections = NULL;

/* Function Prototypes for UDP sending */
struct ESPConnection* initialize_connections(void);
void cleanup_connections(struct ESPConnection* connections);
int send_message(struct ESPConnection* conn, const char* message);

/*=====================*/
/*  Helper Functions   */
/*=====================*/

/* get_color()
 * Returns a color code for the LED pixel at (x, y) based on the game state:
 * - If the pixel falls within the apple's 2×2 block, return 'r'
 * - Else if the pixel is covered by any snake segment's 2×2 block, return 'g'
 * - Otherwise, return 'd' (for gray background)
 */
static char get_color(int x, int y) {
    if (x >= apple.x && x < apple.x + BLOCK_SIZE &&
        y >= apple.y && y < apple.y + BLOCK_SIZE)
        return 'r';
    for (int i = 0; i < snake_length; i++) {
        if (x >= snake[i].x && x < snake[i].x + BLOCK_SIZE &&
            y >= snake[i].y && y < snake[i].y + BLOCK_SIZE)
            return 'g';
    }
    return 'y';
}

/* generate_and_send_esp_messages()
 * For each of the 5 ESP devices, this function builds a message string
 * that covers its 4 assigned strips (columns) of the LED matrix.
 * Each command is formatted as "localStrip.pixelNo&<color>/"
 * where localStrip ranges from 1 to 4 and pixelNo from 1 to 40.
 * The message is then sent via UDP using our send_message() function.
 */
static void generate_and_send_esp_messages(void) {
    char message[4096];  // large buffer for each message
    const int num_esp = NUM_DEVICES;
    const int strips_per_esp = STRIPS_PER_DEVICE;
    
    for (int esp = 0; esp < num_esp; esp++) {
        int offset = 0;
        message[0] = '\0';
        
        /* For each strip assigned to this ESP device.
           Global column = (ESP index * strips_per_esp) + local_strip.
           local_strip is output as (local_strip + 1) to range 1–4.
           Pixel numbers are output as (row + 1) to range 1–40.
        */
        for (int local_strip = 0; local_strip < strips_per_esp; local_strip++) {
            int global_col = esp * strips_per_esp + local_strip;
            for (int row = 0; row < LED_MATRIX_HEIGHT; row++) {
                char command[20];
                char color = get_color(global_col, row);
                int n = snprintf(command, sizeof(command), "%d.%d&%c/", local_strip + 1, row + 1, color);
                if (n < 0 || n >= (int)sizeof(command))
                    continue;
                if (offset + n < (int)sizeof(message)) {
                    memcpy(message + offset, command, n);
                    offset += n;
                    message[offset] = '\0';
                } else {
                    break;
                }
            }
        }
        if (send_message(&esp_connections[esp], message) < 0) {
            fprintf(stderr, "Failed to send message to ESP %d\n", esp + 1);
        } else {
            printf("Message sent to ESP %d: %s\n", esp + 1, message);
        }
    }
}

/*=====================*/
/* UDP Functions       */
/*=====================*/
struct ESPConnection* initialize_connections(void) {
    struct ESPConnection* connections = malloc(NUM_DEVICES * sizeof(struct ESPConnection));
    if (!connections)
        return NULL;
    for (int i = 0; i < NUM_DEVICES; i++) {
        connections[i].socket = socket(AF_INET, SOCK_DGRAM, 0);
        if (connections[i].socket < 0) {
            perror("Socket creation failed");
            cleanup_connections(connections);
            return NULL;
        }
        connections[i].address.sin_family = AF_INET;
        connections[i].address.sin_port = htons(ESP_DEVICES[i].port);
        if (inet_pton(AF_INET, ESP_DEVICES[i].ip, &connections[i].address.sin_addr) <= 0) {
            perror("Invalid address");
            cleanup_connections(connections);
            return NULL;
        }
    }
    return connections;
}

void cleanup_connections(struct ESPConnection* connections) {
    if (connections) {
        for (int i = 0; i < NUM_DEVICES; i++) {
            if (connections[i].socket >= 0)
                close(connections[i].socket);
        }
        free(connections);
    }
}

int send_message(struct ESPConnection* conn, const char* message) {
    size_t message_len = strlen(message);
    return sendto(conn->socket, message, message_len, 0,
                  (struct sockaddr*)&conn->address, sizeof(conn->address));
}

/*=====================*/
/*  Game Functions     */
/*=====================*/

/* reset_game()
 * Resets the game state (snake, apple) after a game-over.
 */
static gboolean
on_close_request(GtkWidget *widget, gpointer user_data) {
    // Quit the application when the window is closed.
    g_application_quit(G_APPLICATION(user_data));
    return GDK_EVENT_STOP; // indicate that we handled the event
}
static gboolean reset_game(gpointer data) {
    (void)data;
    snake_length = 3;
    snake[0].x = (LED_MATRIX_WIDTH / 2 / BLOCK_SIZE) * BLOCK_SIZE;
    snake[0].y = (LED_MATRIX_HEIGHT / 2 / BLOCK_SIZE) * BLOCK_SIZE;
    for (int i = 1; i < snake_length; i++) {
        snake[i].x = snake[0].x - i * BLOCK_SIZE;
        snake[i].y = snake[0].y;
    }
    dx = BLOCK_SIZE;
    dy = 0;
    game_over = false;
    int max_block_x = LED_MATRIX_WIDTH / BLOCK_SIZE;
    int max_block_y = LED_MATRIX_HEIGHT / BLOCK_SIZE;
    int block_x = rand() % max_block_x;
    int block_y = rand() % max_block_y;
    apple.x = block_x * BLOCK_SIZE;
    apple.y = block_y * BLOCK_SIZE;
    gtk_widget_queue_draw(drawing_area);
    return G_SOURCE_REMOVE;
}

/* on_draw()
 * Draws the LED matrix (background, snake, apple) using Cairo.
 */
static void on_draw(GtkDrawingArea *area, cairo_t *cr, int width, int height, gpointer user_data) {
    (void)area; (void)width; (void)height; (void)user_data;
    cairo_set_source_rgb(cr, 0.5, 0.5, 0.5);
    cairo_paint(cr);
    cairo_set_source_rgb(cr, 1.0, 0.0, 0.0);
    cairo_rectangle(cr, apple.x * SCALE, apple.y * SCALE, BLOCK_SIZE * SCALE, BLOCK_SIZE * SCALE);
    cairo_fill(cr);
    cairo_set_source_rgb(cr, 0.0, 1.0, 0.0);
    for (int i = 0; i < snake_length; i++) {
        cairo_rectangle(cr, snake[i].x * SCALE, snake[i].y * SCALE, BLOCK_SIZE * SCALE, BLOCK_SIZE * SCALE);
        cairo_fill(cr);
    }
    cairo_set_source_rgb(cr, 0.3, 0.3, 0.3);
    cairo_set_line_width(cr, 1);
    for (int x = 0; x <= LED_MATRIX_WIDTH; x++) {
        cairo_move_to(cr, x * SCALE, 0);
        cairo_line_to(cr, x * SCALE, LED_MATRIX_HEIGHT * SCALE);
    }
    for (int y = 0; y <= LED_MATRIX_HEIGHT; y++) {
        cairo_move_to(cr, 0, y * SCALE);
        cairo_line_to(cr, LED_MATRIX_WIDTH * SCALE, y * SCALE);
    }
    cairo_stroke(cr);
}

/* game_tick()
 * Called every frame to update the game state and then send UDP messages
 * representing the LED matrix state.
 */
static gboolean game_tick(gpointer data) {
    (void)data;
    if (!game_over) {
        Point prev_positions[MAX_SNAKE];
        for (int i = 0; i < snake_length; i++)
            prev_positions[i] = snake[i];
        snake[0].x += dx;
        snake[0].y += dy;
        if (snake[0].x < 0 || snake[0].x >= LED_MATRIX_WIDTH ||
            snake[0].y < 0 || snake[0].y >= LED_MATRIX_HEIGHT) {
            game_over = true;
            g_print("Game Over: Hit wall\n");
            fflush(stdout);
            g_timeout_add(1500, reset_game, NULL);
            gtk_widget_queue_draw(drawing_area);
        }
        for (int i = 1; i < snake_length; i++)
            snake[i] = prev_positions[i - 1];
        for (int i = 1; i < snake_length; i++) {
            if (snake[0].x == snake[i].x && snake[0].y == snake[i].y) {
                game_over = true;
                g_print("Game Over: Hit self\n");
                fflush(stdout);
                g_timeout_add(1500, reset_game, NULL);
                break;
            }
        }
        if (snake[0].x == apple.x && snake[0].y == apple.y) {
            if (snake_length < MAX_SNAKE) {
                snake[snake_length] = prev_positions[snake_length - 1];
                snake_length++;
            }
            int max_block_x = LED_MATRIX_WIDTH / BLOCK_SIZE;
            int max_block_y = LED_MATRIX_HEIGHT / BLOCK_SIZE;
            int block_x = rand() % max_block_x;
            int block_y = rand() % max_block_y;
            apple.x = block_x * BLOCK_SIZE;
            apple.y = block_y * BLOCK_SIZE;
        }
    }
    gtk_widget_queue_draw(drawing_area);
    generate_and_send_esp_messages();
    return G_SOURCE_CONTINUE;
}

/* on_key_pressed()
 * Handles arrow keys (or WASD) to change the snake's direction and
 * '+'/'-' keys to adjust the frame rate.
 */
static gboolean on_key_pressed(GtkEventControllerKey *controller,
                               guint keyval,
                               guint keycode,
                               GdkModifierType state,
                               gpointer user_data) {
    (void)controller; (void)keycode; (void)state; (void)user_data;
    int old_dx = dx, old_dy = dy;
    switch (keyval) {
        case GDK_KEY_Down:
        case GDK_KEY_s:
            if (old_dy == BLOCK_SIZE) break;
            dx = 0; dy = -BLOCK_SIZE;
            break;
        case GDK_KEY_Up:
        case GDK_KEY_w:
            if (old_dy == -BLOCK_SIZE) break;
            dx = 0; dy = BLOCK_SIZE;
            break;
        case GDK_KEY_Left:
        case GDK_KEY_a:
            if (old_dx == BLOCK_SIZE) break;
            dx = -BLOCK_SIZE; dy = 0;
            break;
        case GDK_KEY_Right:
        case GDK_KEY_d:
            if (old_dx == -BLOCK_SIZE) break;
            dx = BLOCK_SIZE; dy = 0;
            break;
        case GDK_KEY_plus:
        case GDK_KEY_KP_Add:
            if (frames_per_second < 60) {
                frames_per_second++;
                timer_interval_ms = 1000 / frames_per_second;
                g_print("Frame rate increased to %d fps\n", frames_per_second);
            }
            break;
        case GDK_KEY_minus:
        case GDK_KEY_KP_Subtract:
            if (frames_per_second > 1) {
                frames_per_second--;
                timer_interval_ms = 1000 / frames_per_second;
                g_print("Frame rate decreased to %d fps\n", frames_per_second);
            }
            break;
        default:
            break;
    }
    return GDK_EVENT_STOP;
}

/* on_activate()
 * Creates the main window, sets up the drawing area and key event controller,
 * initializes the game state and UDP connections, and starts the game tick timer.
 */
static void on_activate(GtkApplication *app, gpointer user_data) {
    (void)user_data;
    GtkWidget *window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Snake on LED Matrix (GTK4) - Vertical with UDP");
    gtk_window_set_default_size(GTK_WINDOW(window), LED_MATRIX_WIDTH * SCALE, LED_MATRIX_HEIGHT * SCALE);
    g_signal_connect(window, "close-request", G_CALLBACK(on_close_request), app);
    drawing_area = gtk_drawing_area_new();
    gtk_widget_set_size_request(drawing_area, LED_MATRIX_WIDTH * SCALE, LED_MATRIX_HEIGHT * SCALE);
    gtk_drawing_area_set_draw_func(GTK_DRAWING_AREA(drawing_area), on_draw, NULL, NULL);
    gtk_window_set_child(GTK_WINDOW(window), drawing_area);
    GtkEventController *key_controller = gtk_event_controller_key_new();
    gtk_widget_add_controller(window, key_controller);
    g_signal_connect(key_controller, "key-pressed", G_CALLBACK(on_key_pressed), NULL);
    reset_game(NULL);
    esp_connections = initialize_connections();
    if (!esp_connections) {
        fprintf(stderr, "Failed to initialize UDP connections\n");
        exit(EXIT_FAILURE);
    }
    g_timeout_add(timer_interval_ms, game_tick, NULL);
    gtk_widget_show(window);
}

/* Main */
int main(int argc, char *argv[]) {
    GtkApplication *app;
    int status;
    srand((unsigned)time(NULL));
    app = gtk_application_new("com.example.snake", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(on_activate), NULL);
    status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    cleanup_connections(esp_connections);
    return status;
}
