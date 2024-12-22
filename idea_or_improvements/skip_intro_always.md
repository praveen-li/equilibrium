# SKIP INTRO ALWAYS BUTTON FOR STREAMING SERVICES

## Introduction of Idea:
"Currently, streaming services offer viewers the option to 'Skip Intro' for TV series episodes; however, this requires the viewer to manually select the 'Skip Intro' button for each episode. To enhance the viewing experience, this concept proposes the introduction of a new feature: a 'Skip Intro Always' button.

## Purpose of button "SKIP INTRO ALWAYS":
Once the 'Skip Intro Always' button is activated, viewers will automatically skip the intro portion of each episode without needing to interact for every episode. This feature significantly enhances the viewing experience, particularly for those who prefer binge-watching multiple episodes of a TV series in one sitting, as it saves time and eliminates unnecessary button presses.

## Look and Feel
At the start of the intro section for each episode, viewers will be presented with two buttons: 'Skip Intro' and 'Skip Intro Always.' Upon selecting 'Skip Intro Always,' these buttons will no longer appear for subsequent episodes of the same series, streamlining the viewing experience.

Once this button is clicked, the series' homepage, which provides options such as:
- Play from Beginning
- Resume
- More Episodes
can include an additional button labeled 'Do Not Skip Intro.' This button allows viewers to reset the behavior to its default setting, restoring the option to watch the intro for future episodes.

## Example Image of the Pages:
[Page](Link to Image)

## Implementation:
For each episode of a series, the start and end frames for displaying the 'Skip Intro' button are pre-determined. These frames are identified using a video sequencing algorithm that detects recurring video sequences, such as the intro section, at the beginning of each episode. This method is already implemented to accurately mark the intro section.

At the same frame where the 'Skip Intro' button appears, a second button labeled 'Skip Intro Always' will also be displayed. Both buttons will share the same appearance frame, ensuring consistency in their placement and timing.

