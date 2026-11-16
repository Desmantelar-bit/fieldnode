#include "clock_policy.h"

namespace fieldnode {

TimeDecision select_time_source(const bool rtc_present, const bool oscillator_stop,
                                const bool plausible_time, const bool previously_synced) {
  if (!rtc_present || oscillator_stop || !plausible_time || !previously_synced) {
    return {TimeSource::UNSYNCED, false};
  }
  return {TimeSource::RTC, true};
}

const char* time_source_name(const TimeSource source) {
  switch (source) {
    case TimeSource::RTC: return "rtc";
    case TimeSource::GATEWAY: return "gateway";
    case TimeSource::NTP: return "ntp";
    default: return "unsynced";
  }
}

}
