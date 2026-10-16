-- إنشاء الشاشة والواجهة الرئيسية
local ScreenGui = Instance.new("ScreenGui")
local MainFrame = Instance.new("Frame")
local Title = Instance.new("TextLabel")
local SpeedButton = Instance.new("TextButton")
local JumpButton = Instance.new("TextButton")
local ResetButton = Instance.new("TextButton")

-- ربط الواجهة بلاعب اللعبة (CoreGui أو PlayerGui)
ScreenGui.Parent = game:GetService("CoreGui")

-- إعدادات النافذة الرئيسية (Frame)
MainFrame.Name = "MainFrame"
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(35, 35, 35)
MainFrame.Position = UDim2.new(0.3, 0, 0.3, 0)
MainFrame.Size = UDim2.new(0, 220, 0, 240)
MainFrame.Active = true
MainFrame.Draggable = true -- يجعل النافذة قابلة للسحب بالأصبع أو الماوس

-- عنوان القائمة
Title.Name = "Title"
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Font = Enum.Font.SourceSansBold
Title.Text = "My Custom Menu 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 18

-- زر زيادة السرعة
SpeedButton.Name = "SpeedButton"
SpeedButton.Parent = MainFrame
SpeedButton.BackgroundColor3 = Color3.fromRGB(50, 150, 250)
SpeedButton.Position = UDim2.new(0.1, 0, 0.25, 0)
SpeedButton.Size = UDim2.new(0.8, 0, 0, 40)
SpeedButton.Font = Enum.Font.SourceSans
SpeedButton.Text = "Super Speed (50)"
SpeedButton.TextColor3 = Color3.fromRGB(255, 255, 255)
SpeedButton.TextSize = 16

-- زر زيادة القفز
JumpButton.Name = "JumpButton"
JumpButton.Parent = MainFrame
JumpButton.BackgroundColor3 = Color3.fromRGB(50, 200, 100)
JumpButton.Position = UDim2.new(0.1, 0, 0.5, 0)
JumpButton.Size = UDim2.new(0.8, 0, 0, 40)
JumpButton.Font = Enum.Font.SourceSans
JumpButton.Text = "High Jump (100)"
JumpButton.TextColor3 = Color3.fromRGB(255, 255, 255)
JumpButton.TextSize = 16

-- زر إرجاع الإعدادات الطبيعية
ResetButton.Name = "ResetButton"
ResetButton.Parent = MainFrame
ResetButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
ResetButton.Position = UDim2.new(0.1, 0, 0.75, 0)
ResetButton.Size = UDim2.new(0.8, 0, 0, 40)
ResetButton.Font = Enum.Font.SourceSans
ResetButton.Text = "Reset Normal Stats"
ResetButton.TextColor3 = Color3.fromRGB(255, 255, 255)
ResetButton.TextSize = 16

-- ====================
-- البرمجة والأوامر (Functions)
-- ====================

local Player = game.Players.LocalPlayer

-- تفعيل السرعة
SpeedButton.MouseButton1Click:Connect(function()
    if Player.Character and Player.Character:FindFirstChild("Humanoid") then
        Player.Character.Humanoid.WalkSpeed = 50
    end
end)

-- تفعيل القفز
JumpButton.MouseButton1Click:Connect(function()
    if Player.Character and Player.Character:FindFirstChild("Humanoid") then
        Player.Character.Humanoid.JumpPower = 100
    end
end)

-- إعادة السرعة والقفز للوضع الطبيعي
ResetButton.MouseButton1Click:Connect(function()
    if Player.Character and Player.Character:FindFirstChild("Humanoid") then
        Player.Character.Humanoid.WalkSpeed = 16
        Player.Character.Humanoid.JumpPower = 50
    end
end)
