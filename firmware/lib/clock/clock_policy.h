#pragma once

namespace fieldnode {

enum class TimeSource { RTC, GATEWAY, NTP, UNSYNCED };

struct TimeDecision {
  TimeSource source;
  bool trusted;
};

// OSF always wins: a plausible-looking clock is not evidence of validity.
TimeDecision select_time_source(bool rtc_present, bool oscillator_stop,
                                bool plausible_time, bool previously_synced);
const char* time_source_name(TimeSource source);

}
