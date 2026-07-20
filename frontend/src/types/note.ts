export interface Note {
  id: number
  title: string
  content_markdown: string
  topic_id: number | null
  created_at: string
  updated_at: string
}

export interface NoteCreate {
  title: string
  content_markdown?: string
  topic_id?: number | null
}

export interface NoteUpdate {
  title?: string
  content_markdown?: string
  topic_id?: number | null
}
