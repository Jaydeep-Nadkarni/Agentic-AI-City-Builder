local counter = 0

function script:init()
  Debug.toast('Hello World!')
end

function script:update()
  Drawing.setColor(0, 255, 0)
  Drawing.drawText('This is frame ' .. counter, 30, 26)
  Drawing.setColor(255, 255, 255)
  counter = counter + 1
end
