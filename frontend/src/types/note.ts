export interface Note {
  id: string
  title: string
  content_markdown: string
  topic_id: string | null
  created_at: string
  updated_at: string
}

export interface NoteCreate {
  title: string
  content_markdown?: string
  topic_id?: string | null
}

export interface NoteUpdate {
  title?: string
  content_markdown?: string
  topic_id?: string | null
}
