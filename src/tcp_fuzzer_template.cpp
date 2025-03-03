#include <iostream>
#include <cstring>
#include <cstdlib>
#include <unistd.h>
#include <getopt.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <fstream>
#include <string>

void print_usage(const char* prog_name) {
    std::cerr << "Usage: " << prog_name << " [OPTIONS]\n"
              << "Options:\n"
              << "  --target <host:port>    Target in format host:port (required)\n"
              << "  --payload <data>        Payload as string\n"
              << "  --file <filename>       File containing payload\n";
}

std::pair<std::string, int> parse_target(const char* target) {
    std::string target_str(target);
    size_t colon_pos = target_str.find(':');
    if (colon_pos == std::string::npos) {
        throw std::runtime_error("Invalid target format. Use host:port");
    }
    return std::make_pair(target_str.substr(0, colon_pos), std::stoi(target_str.substr(colon_pos + 1)));
}

int main(int argc, char *argv[]) {
    const char *target = nullptr;
    const char *payload = nullptr;
    const char *file_name = nullptr;

    static struct option long_options[] = {
        {"target", required_argument, 0, 't'},
        {"payload", required_argument, 0, 'p'},
        {"file", required_argument, 0, 'f'},
        {0,0,0,0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "t:p:f:", long_options, nullptr)) != -1) {
        switch (opt) {
            case 't': target = optarg; break;
            case 'p': payload = optarg; break;
            case 'f': file_name = optarg; break;
            default: print_usage(argv[0]); return 1;
        }
    }

    if (!target || (!payload && !file_name)) {
        print_usage(argv[0]);
        return 1;
    }

    try {
        auto [host, port] = parse_target(target);
        
        // Get payload data
        std::string data;
        if (payload) {
            data = payload;
        } else {
            std::ifstream file(file_name, std::ios::binary);
            data = std::string((std::istreambuf_iterator<char>(file)),
                               std::istreambuf_iterator<char>());
        }

        // Create and connect socket
        int sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
            perror("socket");
            return 1;
        }

        struct sockaddr_in server_addr = {};
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(port);
        
        if (inet_pton(AF_INET, host.c_str(), &server_addr.sin_addr) <= 0) {
            close(sock);
            return 1;
        }

        // Connect and send immediately
        if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == 0) {
            send(sock, data.c_str(), data.size(), 0);
        }
        
        // Close immediately, don't wait for anything
        close(sock);
        return 0;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
