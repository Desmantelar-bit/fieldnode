#pragma once

#include <Arduino.h>
#include <FS.h>
#include <Preferences.h>

namespace fieldnode {

struct __attribute__((packed)) Rec {
  uint32_t seq;
  uint32_t t_unix;
  uint8_t cls;
  uint16_t len;
  uint8_t body[220];
  uint32_t crc32;
};

static_assert(sizeof(Rec) == 235, "outbox record layout changed");
enum class OutboxClass : uint8_t { A = 0, B = 1, C = 2 };

class Outbox {
 public:
  bool begin(fs::FS& fs, Preferences& preferences);
  bool append(OutboxClass cls, uint32_t seq, uint32_t t_unix,
              const uint8_t* body, size_t len);
  bool peek(OutboxClass cls, Rec& record);
  bool acknowledge(OutboxClass cls, uint32_t cumulative_seq);
  uint32_t ack_cursor(OutboxClass cls) const;
  uint32_t valid_records(OutboxClass cls);
  size_t bytes_used() const;

 private:
  fs::FS* fs_ = nullptr;
  Preferences* preferences_ = nullptr;
  uint32_t cursors_[3] = {0, 0, 0};
  const char* path(OutboxClass cls) const;
  bool read_at(File& file, size_t offset, Rec& record) const;
  static uint32_t crc32(const uint8_t* data, size_t len);
};

}  // namespace fieldnode
