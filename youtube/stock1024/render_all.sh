# 모션그래픽 고화질 렌더 → stock1024/img/<장면>.mp4
cd "$(dirname "$0")/manim"
for s in ${SCENES:-Agenda FriKospi Hynix Flows UsNight Oil Spread Zigzag AiTimeline AiBars Macro BigTwoFlat NextWeek Summary}; do
  nice -n 19 ~/.venvs/manim/bin/manim -qh --fps 30 --disable_caching -o $s scenes.py $s > /dev/null 2>&1 && cp media/videos/scenes/1080p30/$s.mp4 ../img/ && echo $s
done
echo EXIT
