# 1. Basic User Profile & Stats
USER_PROFILE_QUERY = """
query userPublicProfile($username: String!) {
  matchedUser(username: $username) {
    username
    profile {
      ranking
      userAvatar
      realName
      aboutMe
      school
      websites
      countryName
      reputation
    }
  }
}
"""

# 2. Earned & Upcoming Badges
USER_BADGES_QUERY = """
query userBadges($username: String!) {
  matchedUser(username: $username) {
    badges {
      id
      name
      shortName
      icon
    }
    upcomingBadges {
      name
      icon
    }
  }
}
"""

# 3. Submission Calendar (Heatmap)
USER_CALENDAR_QUERY = """
query userSearchCalendar($username: String!, $year: Int) {
  matchedUser(username: $username) {
    userCalendar(year: $year) {     
       activeYears      
       streak      
       totalActiveDays      
       dccBadges {        
       timestamp        
       badge {          
       name          
       icon        
       }      
       }      
       submissionCalendar    
    }
  }
}
"""

# 4. Recent Submissions (Public)
USER_SUBMISSIONS_QUERY = """
query userRecentSubmissions($username: String!, $limit: Int!) {
  recentSubmissionList(username: $username, limit: $limit) {
    title
    titleSlug
    timestamp
    statusDisplay
    lang
  }
}
"""

# 5. Contest Ranking & Performance
USER_CONTEST_QUERY = """
query userContestRankingInfo($username: String!) {
  userContestRanking(username: $username) {
    attendedContestsCount
    rating
    globalRanking
    totalParticipants
    topPercentage
    badge {
      name
    }
  }
}
"""

# 6. Global Problem List
GET_PROBLEMS_QUERY = """
query problemsetQuestionList(
  $categorySlug: String, 
  $limit: Int, 
  $skip: Int, 
  $filters: QuestionListFilterInput
) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    total: totalNum
    questions: data {
      title
      titleSlug
      acRate
      difficulty
      status
      isFavor
      hasSolution
      hasVideoSolution
      paidOnly: isPaidOnly
      frontendQuestionId: questionFrontendId
      topicTags {
        name
        id
        slug
      }
    }
  }
}
"""
DAILY_QUESTION_QUERY = """
query questionOfToday {
  activeDailyCodingChallengeQuestion {
    date
    link
    question {
      questionId
      title
      difficulty
      content
    }
  }
}
"""

USER_AC_SUBMISSIONS_QUERY = """
query userRecentAcSubmissions($username: String!, $limit: Int!) {
  recentAcSubmissionList(username: $username, limit: $limit) {
    id
    title
    titleSlug
    timestamp
  }
}
"""

USER_SUBMISSION_LIST_QUERY = """
query submissionList($offset: Int!, $limit: Int!) {
  submissionList(offset: $offset, limit: $limit) {
    hasNext
    submissions {
      title
      titleSlug
      statusDisplay
      timestamp
      lang
    }
  }
}
"""

GET_PROBLEMS_QUERY = """
query problemsetQuestionList(
  $categorySlug: String,
  $limit: Int,
  $skip: Int,
  $filters: QuestionListFilterInput
) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    questions: data {
      title
      titleSlug
      difficulty
      topicTags {
        name
        slug
      }
    }
  }
}
"""
QUESTION_TITLE_QUERY = """
query questionTitle($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title
    titleSlug
  }
}
"""

FULL_SOLVED_LIST_QUERY = """
query userSolvedProblems($categorySlug: String, $skip: Int, $limit: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    skip: $skip
    limit: $limit
    filters: $filters
  ) {
    totalNum
    questions: data {
      titleSlug
    }
  }
}
"""

QUESTION_TITLE_QUERY = """
query questionTitle($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title
    titleSlug
  }
}
"""