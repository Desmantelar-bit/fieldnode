#include "outbox.h"

#include <cstring>

namespace fieldnode {
namespace {
constexpr char kPaths[][16] = {"/outbox_a.bin", "/outbox_b.bin", "/outbox_c.bin"};
constexpr char kCursorKeys[][8] = {"ack_a", "ack_b", "ack_c"};
int index_of(const OutboxClass cls) { return static_cast<int>(cls); }
}

const char* Outbox::path(const OutboxClass cls) const { return kPaths[index_of(cls)]; }

uint32_t Outbox::crc32(const uint8_t* data, const size_t len) {
  uint32_t crc = 0xFFFFFFFFU;
  for (size_t i = 0; i < len; ++i) {
    crc ^= data[i];
    for (uint8_t bit = 0; bit < 8; ++bit) crc = (crc >> 1) ^ (0xEDB88320U & (0U - (crc & 1U)));
  }
  return ~crc;
}

bool Outbox::begin(fs::FS& fs, Preferences& preferences) {
  fs_ = &fs;
  preferences_ = &preferences;
  if (!preferences_->begin("outbox", false)) return false;
  for (int i = 0; i < 3; ++i) cursors_[i] = preferences_->getUInt(kCursorKeys[i], 0);
  for (int i = 0; i < 3; ++i) {
    if (!fs_->exists(kPaths[i])) {
      File file = fs_->open(kPaths[i], FILE_WRITE);
      if (!file) return false;
      file.flush();
      file.close();
    }
  }
  return true;
}

bool Outbox::append(const OutboxClass cls, const uint32_t seq, const uint32_t t_unix,
                    const uint8_t* body, const size_t len) {
  if (fs_ == nullptr || body == nullptr || len > sizeof(Rec::body) || seq == 0) return false;
  Rec record{};
  record.seq = seq;
  record.t_unix = t_unix;
  record.cls = static_cast<uint8_t>(cls);
  record.len = static_cast<uint16_t>(len);
  memcpy(record.body, body, len);
  record.crc32 = crc32(reinterpret_cast<const uint8_t*>(&record), sizeof(record) - sizeof(record.crc32));
  File file = fs_->open(path(cls), FILE_APPEND);
  if (!file) return false;
  const size_t written = file.write(reinterpret_cast<const uint8_t*>(&record), sizeof(record));
  file.flush();
  file.close();
  return written == sizeof(record);
}

bool Outbox::read_at(File& file, const size_t offset, Rec& record) const {
  if (offset + sizeof(record) > file.size()) return false;
  if (!file.seek(offset, SeekSet)) return false;
  if (file.read(reinterpret_cast<uint8_t*>(&record), sizeof(record)) != sizeof(record)) return false;
  if (record.cls > static_cast<uint8_t>(OutboxClass::C) || record.len > sizeof(record.body)) return false;
  const uint32_t expected = crc32(reinterpret_cast<const uint8_t*>(&record), sizeof(record) - sizeof(record.crc32));
  return expected == record.crc32;
}

bool Outbox::peek(const OutboxClass cls, Rec& record) {
  if (fs_ == nullptr) return false;
  File file = fs_->open(path(cls), FILE_READ);
  if (!file) return false;
  for (size_t offset = 0; offset + sizeof(Rec) <= file.size(); offset += sizeof(Rec)) {
    Rec candidate{};
    if (!read_at(file, offset, candidate)) continue;
    if (candidate.seq > cursors_[index_of(cls)]) { record = candidate; file.close(); return true; }
  }
  file.close();
  return false;
}

bool Outbox::acknowledge(const OutboxClass cls, const uint32_t cumulative_seq) {
  const int index = index_of(cls);
  if (preferences_ == nullptr || cumulative_seq <= cursors_[index]) return true;
  cursors_[index] = cumulative_seq;
  return preferences_->putUInt(kCursorKeys[index], cumulative_seq) == sizeof(uint32_t);
}

uint32_t Outbox::ack_cursor(const OutboxClass cls) const { return cursors_[index_of(cls)]; }

uint32_t Outbox::valid_records(const OutboxClass cls) {
  if (fs_ == nullptr) return 0;
  File file = fs_->open(path(cls), FILE_READ);
  if (!file) return 0;
  uint32_t count = 0;
  for (size_t offset = 0; offset + sizeof(Rec) <= file.size(); offset += sizeof(Rec)) {
    Rec record{};
    if (read_at(file, offset, record) && record.seq > ack_cursor(cls)) ++count;
  }
  file.close();
  return count;
}

size_t Outbox::bytes_used() const {
  if (fs_ == nullptr) return 0;
  size_t total = 0;
  for (const char* item : kPaths) {
    File file = fs_->open(item, FILE_READ);
    if (file) { total += file.size(); file.close(); }
  }
  return total;
}
}  // namespace fieldnode
