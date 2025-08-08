"""
Streamlit application for extracting transcripts from YouTube videos.

This small web app provides a single text field for the user to paste
a YouTube video URL. After pressing the button, the app fetches
the transcript using the ``youtube transcript api`` library and
displays it in a scrollable text area. A download button allows
the transcript to be saved as a simple ``.txt`` file.

To run this app locally use:

    streamlit run app.py

The app is intentionally minimal to make it easy to host on platforms
like Streamlit Community Cloud. Users can copy or download the
transcript directly from their browser. For automatic copy to the
clipboard in the browser you would need additional JavaScript;
this basic version opts for manual copy via a text area.
"""

import re
from typing import Optional

import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> Optional[str]:
    """Extract the YouTube video ID from a variety of URL formats.

    Args:
        url: A full YouTube URL or just the video ID.

    Returns:
        The video ID if found, else ``None``.
    """
    # Regular expression covers standard YouTube links and the shorter youtu.be format
    pattern = r"(?:v=|/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def fetch_transcript(video_id: str) -> str:
    """Fetch the transcript for the given YouTube video ID.

    The function concatenates all transcript segments into one string,
    separating each line by a newline character.

    Args:
        video_id: The 11-character ID of the YouTube video.

    Returns:
        The full transcript as a string.

    Raises:
        Exception: If fetching the transcript fails for any reason.
    """
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    return "\n".join(entry["text"] for entry in transcript_list)


def main() -> None:
    """Main entry point for the Streamlit app."""
    st.set_page_config(page_title="YouTube Transcript Copier", page_icon="📋")
    st.title("YouTube Transcript Copier")
    st.write(
        "Paste a YouTube video URL below and click **Get Transcript** to fetch its"
        " captions as text. You can then download the transcript as a file or copy"
        " the text manually from the box."
    )

    # Input field for the YouTube link
    video_url = st.text_input(
        "Enter YouTube Video URL:",
        placeholder="https://www.youtube.com/watch?v=example",
        key="video_url",
    )

    # Button to trigger the fetch
    if st.button("Get Transcript", key="fetch_button"):
        if not video_url:
            st.error("Please enter a YouTube URL.")
            return

        video_id = extract_video_id(video_url)
        if video_id is None:
            st.error("Invalid YouTube URL. Please check the link and try again.")
            return

        # Attempt to fetch the transcript
        with st.spinner("Fetching transcript..."):
            try:
                transcript = fetch_transcript(video_id)
            except Exception as exc:
                st.error(
                    f"Sorry, there was a problem fetching the transcript: {exc}."
                )
                return

        # Display and provide download
        st.success("Transcript fetched successfully!")
        st.write("Below is the transcript of your video. You can scroll and copy.")
        st.text_area(
            "Transcript", transcript, height=300, help="Click inside and press Ctrl+A to select all."
        )
        st.download_button(
            label="Download Transcript as .txt",
            data=transcript,
            file_name="youtube_transcript.txt",
            mime="text/plain",
        )


if __name__ == "__main__":
    main()
