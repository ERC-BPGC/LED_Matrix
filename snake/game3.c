#include <gtk/gtk.h>
#include <stdlib.h>
#include <time.h>
#include <stdio.h>
#include <string.h>
#include <arpa/inet.h>
#include <unistd.h>

//-------------------------------------------------------------------
// LED Matrix and Game Parameters
//-------------------------------------------------------------------
// LED matrix is 40 columns (wide) x 20 rows (tall).
// Paddles lie along the top (row 0) and bottom (row MATRIX_HEIGHT-1).
#define MATRIX_WIDTH 20
#define MATRIX_HEIGHT 40
// For horizontal paddles:
//   - Thickness (vertical size) is 2
//   - Length (horizontal size) is 5
#define PADDLE_THICKNESS 2
#define PADDLE_LENGTH    5
#define BALL_WIDTH 2
#define BALL_HEIGHT 2

//-------------------------------------------------------------------
// UDP Sending Configuration (ESP Devices)
//-------------------------------------------------------------------
#define NUM_DEVICES 5
#define STRIPS_PER_DEVICE 4
#define MAX_MESSAGE_LEN 2048

typedef struct {
    const char* ip;
    int port;
    int first_strip_number;  // starting global strip number (1-indexed), if needed
} ESPConfig;

static const ESPConfig ESP_DEVICES[NUM_DEVICES] = {
    {"172.20.10.2", 12345, 1},
    {"192.168.120.115", 12342, 5},
    {"192.168.120.53", 12343, 9},
    {"192.168.120.54", 12344, 13},
    {"192.168.120.109", 12345, 17}
};

typedef struct {
    int socket;
    struct sockaddr_in address;
} ESPConnection;

ESPConnection* esp_connections = NULL;

ESPConnection* initialize_connections(void) {
    ESPConnection* connections = malloc(NUM_DEVICES * sizeof(ESPConnection));
    if (!connections)
        return NULL;
    for (int i = 0; i < NUM_DEVICES; i++) {
        connections[i].socket = socket(AF_INET, SOCK_DGRAM, 0);
        if (connections[i].socket < 0) {
            perror("Socket creation failed");
            free(connections);
            return NULL;
        }
        connections[i].address.sin_family = AF_INET;
        connections[i].address.sin_port = htons(ESP_DEVICES[i].port);
        if (inet_pton(AF_INET, ESP_DEVICES[i].ip, &connections[i].address.sin_addr) <= 0) {
            perror("Invalid address");
            free(connections);
            return NULL;
        }
    }
    return connections;
}

void cleanup_connections(ESPConnection* connections) {
    if (connections) {
        for (int i = 0; i < NUM_DEVICES; i++) {
            if (connections[i].socket >= 0)
                close(connections[i].socket);
        }
        free(connections);
    }
}

int send_message(ESPConnection* conn, const char* message) {
    size_t message_len = strlen(message);
    return sendto(conn->socket, message, message_len, 0,
                  (struct sockaddr*)&conn->address, sizeof(conn->address));
}

//-------------------------------------------------------------------
// Pong Game Structure
//-------------------------------------------------------------------
typedef struct {
    GtkWidget *window;
    GtkWidget *grid;
    GtkWidget *cells[MATRIX_HEIGHT][MATRIX_WIDTH];
    
    // For horizontal paddles: top paddle at row 0, bottom paddle at row MATRIX_HEIGHT-1.
    // Their x positions determine where the paddle starts horizontally.
    int top_paddle_x;
    int bottom_paddle_x;
    
    // Ball position and velocity.
    int ball_x;
    int ball_y;
    int ball_dx;
    int ball_dy;
    
    // Flash state.
    gboolean flash_active;
    GdkRGBA flash_color;
    
    // Scoring.
    int blue_score;
    int red_score;
    
    int frame_rate;
    guint timer_id;
} PongGame;

PongGame game;

//-------------------------------------------------------------------
// Flash Functions
//-------------------------------------------------------------------
static gboolean clear_flash(gpointer data) {
    (void)data;
    game.flash_active = FALSE;
    gtk_widget_queue_draw(game.window);
    return G_SOURCE_REMOVE;
}

void flash_screen(const gchar *hex_color, int duration_ms) {
    if (!gdk_rgba_parse(&game.flash_color, hex_color)) {
        g_warning("Invalid color format: %s", hex_color);
        return;
    }
    game.flash_active = TRUE;
    gtk_widget_queue_draw(game.window);
    g_timeout_add(duration_ms, clear_flash, NULL);
}

//-------------------------------------------------------------------
// Reset Game State after a goal
//-------------------------------------------------------------------
void reset_game(void) {
    // Reset paddles to center.
    game.top_paddle_x = (MATRIX_WIDTH - PADDLE_LENGTH) / 2;
    game.bottom_paddle_x = (MATRIX_WIDTH - PADDLE_LENGTH) / 2;
    // Reset ball to center.
    game.ball_x = MATRIX_WIDTH / 2;
    game.ball_y = MATRIX_HEIGHT / 2;
    // Randomize ball direction.
    game.ball_dx = (rand() % 2) ? 1 : -1;
    game.ball_dy = (rand() % 2) ? 1 : -1;
}

//-------------------------------------------------------------------
// LED/ESP Message Generation
//-------------------------------------------------------------------
/*
 * get_color()
 * Determines the color code for the LED at global coordinate (x, y).
 * Returns:
 *   - 'b' if the pixel belongs to the top paddle (row 0)
 *   - 'r' if the pixel belongs to the bottom paddle (row MATRIX_HEIGHT-1)
 *   - 'g' if the pixel is occupied by the ball
 *   - 'd' for the background.
 * 
 * If flash is active, all pixels will be drawn with the flash color.
 */
static char get_color(int x, int y) {
    if (game.flash_active)
        return game.flash_color.red > 0.5 ? 'r' : 'b'; // Placeholder for flash.
    /* Ball takes precedence. */
    if (x >= game.ball_x && x < game.ball_x + BALL_WIDTH &&
        y >= game.ball_y && y < game.ball_y + BALL_HEIGHT)
        return 'g';
    /* Top paddle: row 0, spans from game.top_paddle_x to game.top_paddle_x + PADDLE_LENGTH - 1. */
    if (y == 0 && x >= game.top_paddle_x && x < game.top_paddle_x + PADDLE_LENGTH)
        return 'b';
    /* Bottom paddle: row MATRIX_HEIGHT-1. */
    if (y == MATRIX_HEIGHT - 1 && x >= game.bottom_paddle_x && x < game.bottom_paddle_x + PADDLE_LENGTH)
        return 'r';
    return 'd';
}

/*
 * generate_and_send_esp_messages()
 *
 * For each ESP device, iterate over its 4 local LED strips.
 * Each local strip corresponds to a global column calculated as:
 *     global_col = (esp_index * STRIPS_PER_DEVICE) + local_strip.
 * For each strip, iterate over MATRIX_HEIGHT rows (pixels 1–MATRIX_HEIGHT) and build a command string
 * of the form "stripno.pixelno&color/" where:
 *    - stripno is (local_strip+1) [range 1–4],
 *    - pixelno is (row+1) [range 1–MATRIX_HEIGHT],
 *    - color is determined by get_color().
 * The complete message is then sent via UDP.
 */
static void generate_and_send_esp_messages(void) {
    char message[4096];
    const int strips_per_esp = STRIPS_PER_DEVICE;
    for (int esp = 0; esp < NUM_DEVICES; esp++) {
        int offset = 0;
        message[0] = '\0';
        for (int local_strip = 0; local_strip < strips_per_esp; local_strip++) {
            int global_col = esp * strips_per_esp + local_strip;
            for (int row = 0; row < MATRIX_HEIGHT; row++) {
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
            printf("ESP %d message: %s\n\n", esp + 1, message);
        }
    }
}

//-------------------------------------------------------------------
// Game Logic: Update Game State
//-------------------------------------------------------------------
static gboolean update_game_state(gpointer data) {
    (void)data;
    /* Update ball position. */
    game.ball_x += game.ball_dx;
    game.ball_y += game.ball_dy;
    
    /* Bounce off the left/right walls. */
    if (game.ball_x <= 0 || game.ball_x + BALL_WIDTH >= MATRIX_WIDTH)
        game.ball_dx *= -1;
    
    /* Check for scoring:
       - If ball goes above row 0, blue (top paddle) scores.
       - If ball goes below row MATRIX_HEIGHT, red (bottom paddle) scores.
    */
    if (game.ball_y < 0) {
        game.blue_score++;
        flash_screen("#0000FF", 2000); // Flash blue for 2 seconds.
        reset_game();
    } else if (game.ball_y + BALL_HEIGHT > MATRIX_HEIGHT) {
        game.red_score++;
        flash_screen("#FF0000", 2000); // Flash red for 2 seconds.
        reset_game();
    }
    
    /* Bounce off the top paddle.
       Check if any part of the ball overlaps the paddle region.
    */
    if (game.ball_y <= PADDLE_THICKNESS &&
        game.ball_x + BALL_WIDTH > game.top_paddle_x &&
        game.ball_x < game.top_paddle_x + PADDLE_LENGTH) {
        game.ball_dy = abs(game.ball_dy); // Ensure ball moves downward.
    }
    
    /* Bounce off the bottom paddle.
       Check if any part of the ball overlaps the paddle region.
    */
    if (game.ball_y + BALL_HEIGHT >= MATRIX_HEIGHT - PADDLE_THICKNESS &&
        game.ball_x + BALL_WIDTH > game.bottom_paddle_x &&
        game.ball_x < game.bottom_paddle_x + PADDLE_LENGTH) {
        game.ball_dy = -abs(game.ball_dy); // Ensure ball moves upward.
    }
    
    /* Send current LED state via UDP. */
    generate_and_send_esp_messages();
    
    /* Redraw the GTK window. */
    gtk_widget_queue_draw(game.window);
    return G_SOURCE_CONTINUE;
}

//-------------------------------------------------------------------
// Draw Function for GTK Grid Visualization
//-------------------------------------------------------------------
static gboolean draw_cell(GtkWidget *widget, cairo_t *cr, gpointer data) {
    int x = GPOINTER_TO_INT(g_object_get_data(G_OBJECT(widget), "x"));
    int y = GPOINTER_TO_INT(g_object_get_data(G_OBJECT(widget), "y"));
    char c = get_color(x, y);
    GdkRGBA color = {0, 0, 0, 1};
    switch (c) {
        case 'b': gdk_rgba_parse(&color, "#0000FF"); break;
        case 'r': gdk_rgba_parse(&color, "#FF0000"); break;
        case 'g': gdk_rgba_parse(&color, "#00FF00"); break;
        default:  gdk_rgba_parse(&color, "#000000"); break;
    }
    gtk_render_background(gtk_widget_get_style_context(widget), cr, 0, 0,
                          gtk_widget_get_allocated_width(widget),
                          gtk_widget_get_allocated_height(widget));
    gdk_cairo_set_source_rgba(cr, &color);
    cairo_paint(cr);
    return FALSE;
}

//-------------------------------------------------------------------
// Key Press Event: Move Paddles
//-------------------------------------------------------------------
// Top paddle: use W (move left) and S (move right)
// Bottom paddle: use I (move left) and K (move right)
static gboolean key_press_event(GtkWidget *widget, GdkEventKey *event, gpointer data) {
    (void)widget; (void)data;
    switch (event->keyval) {
        case GDK_KEY_w:
            if (game.top_paddle_x > 0)
                game.top_paddle_x--;
            break;
        case GDK_KEY_s:
            if (game.top_paddle_x + PADDLE_LENGTH < MATRIX_WIDTH)
                game.top_paddle_x++;
            break;
        case GDK_KEY_i:
            if (game.bottom_paddle_x > 0)
                game.bottom_paddle_x--;
            break;
        case GDK_KEY_k:
            if (game.bottom_paddle_x + PADDLE_LENGTH < MATRIX_WIDTH)
                game.bottom_paddle_x++;
            break;
    }
    return TRUE;
}

//-------------------------------------------------------------------
// GTK Application Activation
//-------------------------------------------------------------------
static void activate(GtkApplication *app, gpointer user_data) {
    (void)user_data;
    game.window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(game.window), "UDP Pong Game (Rotated Paddles)");
    gtk_window_set_default_size(GTK_WINDOW(game.window), 400, 800);
    
    /* Create a grid to visualize the LED matrix. */
    game.grid = gtk_grid_new();
    gtk_container_add(GTK_CONTAINER(game.window), game.grid);
    for (int y = 0; y < MATRIX_HEIGHT; y++) {
        for (int x = 0; x < MATRIX_WIDTH; x++) {
            GtkWidget *cell = gtk_drawing_area_new();
            gtk_widget_set_size_request(cell, 20, 20);
            g_object_set_data(G_OBJECT(cell), "x", GINT_TO_POINTER(x));
            g_object_set_data(G_OBJECT(cell), "y", GINT_TO_POINTER(y));
            g_signal_connect(cell, "draw", G_CALLBACK(draw_cell), NULL);
            gtk_grid_attach(GTK_GRID(game.grid), cell, x, y, 1, 1);
        }
    }
    
    g_signal_connect(game.window, "key-press-event", G_CALLBACK(key_press_event), NULL);
    
    /* Initialize game state. */
    game.top_paddle_x = (MATRIX_WIDTH - PADDLE_LENGTH) / 2;
    game.bottom_paddle_x = (MATRIX_WIDTH - PADDLE_LENGTH) / 2;
    game.ball_x = MATRIX_WIDTH / 2;
    game.ball_y = MATRIX_HEIGHT / 2;
    game.ball_dx = (rand() % 2) ? 1 : -1;
    game.ball_dy = (rand() % 2) ? 1 : -1;
    game.frame_rate = 10;
    game.flash_active = FALSE;
    game.blue_score = 0;
    game.red_score = 0;
    
    game.timer_id = g_timeout_add(1000 / game.frame_rate, update_game_state, NULL);
    gtk_widget_show_all(game.window);
}

int main(int argc, char **argv) {
    srand(time(NULL));
    esp_connections = initialize_connections();
    GtkApplication *app = gtk_application_new("org.example.udppong", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    cleanup_connections(esp_connections);
    return status;
}
