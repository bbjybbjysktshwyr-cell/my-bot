-- إنشاء الشاشة والواجهة الرئيسية
local ScreenGui = Instance.new("ScreenGui")
local MainFrame = Instance.new("Frame")
local Title = Instance.new("TextLabel")
local ToggleButton = Instance.new("TextButton")
local SpeedInput = Instance.new("TextBox")
local SpeedLabel = Instance.new("TextLabel")
local RespawnButton = Instance.new("TextButton")

-- ربط الواجهة بلاعب اللعبة
ScreenGui.Parent = game:GetService("CoreGui")
ScreenGui.Name = "SpeedHackGui"

-- إعدادات النافذة الرئيسية
MainFrame.Name = "MainFrame"
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(25, 25, 25)
MainFrame.Position = UDim2.new(0.35, 0, 0.3, 0)
MainFrame.Size = UDim2.new(0, 220, 0, 230)
MainFrame.Active = true
MainFrame.Draggable = true

-- عنوان القائمة
Title.Name = "Title"
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(15, 15, 15)
Title.Size = UDim2.new(1, 0, 0, 35)
Title.Font = Enum.Font.SourceSansBold
Title.Text = "Diamond Store"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 18

-- عنوان السرعة
SpeedLabel.Name = "SpeedLabel"
SpeedLabel.Parent = MainFrame
SpeedLabel.BackgroundTransparency = 1
SpeedLabel.Position = UDim2.new(0.1, 0, 0.2, 0)
SpeedLabel.Size = UDim2.new(0.8, 0, 0, 20)
SpeedLabel.Font = Enum.Font.SourceSans
SpeedLabel.Text = "أدخل قيمة السرعة المطلوبة:"
SpeedLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
SpeedLabel.TextSize = 14

-- مربّع تحديد قيمة السرعة
SpeedInput.Name = "SpeedInput"
SpeedInput.Parent = MainFrame
SpeedInput.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
SpeedInput.Position = UDim2.new(0.1, 0, 0.32, 0)
SpeedInput.Size = UDim2.new(0.8, 0, 0, 35)
SpeedInput.Font = Enum.Font.SourceSansBold
SpeedInput.Text = "50"
SpeedInput.TextColor3 = Color3.fromRGB(0, 255, 150)
SpeedInput.TextSize = 18

-- زر تشغيل وإيقاف السرعة
ToggleButton.Name = "ToggleButton"
ToggleButton.Parent = MainFrame
ToggleButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
ToggleButton.Position = UDim2.new(0.1, 0, 0.52, 0)
ToggleButton.Size = UDim2.new(0.8, 0, 0, 35)
ToggleButton.Font = Enum.Font.SourceSansBold
ToggleButton.Text = "إيقاف [OFF]"
ToggleButton.TextColor3 = Color3.fromRGB(255, 255, 255)
ToggleButton.TextSize = 16

-- زر إعادة التوليد (Respawn)
RespawnButton.Name = "RespawnButton"
RespawnButton.Parent = MainFrame
RespawnButton.BackgroundColor3 = Color3.fromRGB(120, 50, 200)
RespawnButton.Position = UDim2.new(0.1, 0, 0.75, 0)
RespawnButton.Size = UDim2.new(0.8, 0, 0, 40)
RespawnButton.Font = Enum.Font.SourceSansBold
RespawnButton.Text = "إعادة توليد (Respawn)"
RespawnButton.TextColor3 = Color3.fromRGB(255, 255, 255)
RespawnButton.TextSize = 15

-- =========================================
-- منطق البرمجة والأزرار
-- =========================================

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local LocalPlayer = Players.LocalPlayer

local isSpeedActive = false
local speedConnection = nil

-- وظيفة السرعة
local function applySpeed()
    if isSpeedActive and LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("Humanoid") then
        local humanoid = LocalPlayer.Character.Humanoid
        local desiredSpeed = tonumber(SpeedInput.Text) or 50
        
        humanoid.WalkSpeed = desiredSpeed
        
        if humanoid.MoveDirection.Magnitude > 0 then
            LocalPlayer.Character:TranslateBy(humanoid.MoveDirection * (desiredSpeed / 100))
        end
    end
end

-- زر التشغيل والإيقاف
ToggleButton.MouseButton1Click:Connect(function()
    isSpeedActive = not isSpeedActive
    
    if isSpeedActive then
        ToggleButton.Text = "تشغيل [ON]"
        ToggleButton.BackgroundColor3 = Color3.fromRGB(50, 200, 80)
        
        if speedConnection then speedConnection:Disconnect() end
        speedConnection = RunService.RenderStepped:Connect(applySpeed)
    else
        ToggleButton.Text = "إيقاف [OFF]"
        ToggleButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
        
        if speedConnection then 
            speedConnection:Disconnect() 
            speedConnection = nil
        end
        
        if LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("Humanoid") then
            LocalPlayer.Character.Humanoid.WalkSpeed = 16
        end
    end
end)

-- زر الريسبون (إعادة التوليد)
RespawnButton.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("Humanoid") then
        char.Humanoid.Health = 0
    end
end)
