export type StudyMethod =
  | "active_recall"
  | "spaced_repetition"
  | "practice_testing"
  | "interleaving"
  | "elaborative_interrogation"
  | "dual_coding"
  | "self_explanation"
  | "feynman_technique"
  | "pomodoro";

export type StudyChallenge =
  | "remembering_information"
  | "understanding_concepts"
  | "staying_focused"
  | "procrastination"
  | "knowing_what_to_study"
  | "preparing_for_tests"
  | "managing_multiple_subjects"
  | "staying_consistent";

export interface StudentContext {
  student_id: string;
  subject: string;
  topic?: string;
  primary_challenge: StudyChallenge;
  last_method_used?: string;
  recent_quiz_scores?: number[];
  forgets_over_time?: boolean;
  strong_on_single_topics?: boolean;
  confidence_level?: "low" | "medium" | "high";
  days_until_assessment?: number;
  minutes_available?: number;
}

export interface MethodRecommendation {
  methods: StudyMethod[];
  reasoning: string;
  confidence: number;
}

export const STUDY_CHALLENGES: { value: StudyChallenge; label: string }[] = [
  { value: "remembering_information", label: "Remembering information" },
  { value: "understanding_concepts", label: "Understanding concepts" },
  { value: "staying_focused", label: "Staying focused" },
  { value: "procrastination", label: "Procrastination" },
  { value: "knowing_what_to_study", label: "Knowing what to study" },
  { value: "preparing_for_tests", label: "Preparing for tests" },
  { value: "managing_multiple_subjects", label: "Managing multiple subjects" },
  { value: "staying_consistent", label: "Staying consistent" },
];

export const METHOD_LABELS: Record<StudyMethod, string> = {
  active_recall: "Active Recall",
  spaced_repetition: "Spaced Repetition",
  practice_testing: "Practice Testing",
  interleaving: "Interleaving",
  elaborative_interrogation: "Elaborative Interrogation",
  dual_coding: "Dual Coding",
  self_explanation: "Self-Explanation",
  feynman_technique: "Feynman Technique",
  pomodoro: "Pomodoro",
};