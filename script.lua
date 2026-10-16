-- استخدام PlayerGui لضمان ظهور الواجهة بكل الأجهزة
local Players = game:GetService("Players")
local LocalPlayer = Players.LocalPlayer
local PlayerGui = LocalPlayer:WaitForChild("PlayerGui")
local RunService = game:GetService("RunService")

-- إزالة الواجهة القديمة إن وجدت
if PlayerGui:FindFirstChild("SpeedHackGui") then
    PlayerGui.SpeedHackGui:Destroy()
end

-- إنشاء الشاشة والواجهة الرئيسية
local ScreenGui = Instance.new("ScreenGui")
local MainFrame = Instance.new("Frame")
local Title = Instance.new("TextLabel")
local ToggleButton = Instance.new("TextButton")
local SpeedInput = Instance.new("TextBox")
local SpeedLabel = Instance.new("TextLabel")
local RespawnButton = Instance.new("TextButton")
local TeleportButton = Instance.new("TextButton")

-- أزرار تحديد نوع البيض
local AnyEggBtn = Instance.new("TextButton")
local MythicalBtn = Instance.new("TextButton")
local DivineBtn = Instance.new("TextButton")
local SecretBtn = Instance.new("TextButton")

ScreenGui.Name = "SpeedHackGui"
ScreenGui.Parent = PlayerGui
ScreenGui.ResetOnSpawn = false

-- إعدادات النافذة
MainFrame.Name = "MainFrame"
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(25, 25, 25)
MainFrame.Position = UDim2.new(0.3, 0, 0.2, 0)
MainFrame.Size = UDim2.new(0, 240, 0, 420)
MainFrame.Active = true
MainFrame.Draggable = true

-- عنوان القائمة
Title.Name = "Title"
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(15, 15, 15)
Title.Size = UDim2.new(1, 0, 0, 35)
Title.Font = Enum.Font.SourceSansBold
Title.Text = "Steal An Egg Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 18

-- عنوان السرعة
SpeedLabel.Name = "SpeedLabel"
SpeedLabel.Parent = MainFrame
SpeedLabel.BackgroundTransparency = 1
SpeedLabel.Position = UDim2.new(0.1, 0, 0.09, 0)
SpeedLabel.Size = UDim2.new(0.8, 0, 0, 20)
SpeedLabel.Font = Enum.Font.SourceSans
SpeedLabel.Text = "قيمة السرعة الآمنة:"
SpeedLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
SpeedLabel.TextSize = 13

-- مربّع تحديد السرعة
SpeedInput.Name = "SpeedInput"
SpeedInput.Parent = MainFrame
SpeedInput.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
SpeedInput.Position = UDim2.new(0.1, 0, 0.15, 0)
SpeedInput.Size = UDim2.new(0.8, 0, 0, 28)
SpeedInput.Font = Enum.Font.SourceSansBold
SpeedInput.Text = "35"
SpeedInput.TextColor3 = Color3.fromRGB(0, 255, 150)
SpeedInput.TextSize = 16

-- زر تشغيل وإيقاف السرعة
ToggleButton.Name = "ToggleButton"
ToggleButton.Parent = MainFrame
ToggleButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
ToggleButton.Position = UDim2.new(0.1, 0, 0.25, 0)
ToggleButton.Size = UDim2.new(0.8, 0, 0, 32)
ToggleButton.Font = Enum.Font.SourceSansBold
ToggleButton.Text = "تشغيل السرعة [OFF]"
ToggleButton.TextColor3 = Color3.fromRGB(255, 255, 255)
ToggleButton.TextSize = 14

-- زر التليبرورت لمنطقة الأمان
TeleportButton.Name = "TeleportButton"
TeleportButton.Parent = MainFrame
TeleportButton.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
TeleportButton.Position = UDim2.new(0.1, 0, 0.36, 0)
TeleportButton.Size = UDim2.new(0.8, 0, 0, 32)
TeleportButton.Font = Enum.Font.SourceSansBold
TeleportButton.Text = "منطقة الأمان (Spawn)"
TeleportButton.TextColor3 = Color3.fromRGB(255, 255, 255)
TeleportButton.TextSize = 13

-- زر سرقة أي بيضة
AnyEggBtn.Name = "AnyEggBtn"
AnyEggBtn.Parent = MainFrame
AnyEggBtn.BackgroundColor3 = Color3.fromRGB(80, 80, 80)
AnyEggBtn.Position = UDim2.new(0.1, 0, 0.47, 0)
AnyEggBtn.Size = UDim2.new(0.8, 0, 0, 30)
AnyEggBtn.Font = Enum.Font.SourceSansBold
AnyEggBtn.Text = "سرقة أي بيضة 🥚"
AnyEggBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
AnyEggBtn.TextSize = 13

-- زر سرقة بيض Mythical
MythicalBtn.Name = "MythicalBtn"
MythicalBtn.Parent = MainFrame
MythicalBtn.BackgroundColor3 = Color3.fromRGB(150, 50, 200)
MythicalBtn.Position = UDim2.new(0.1, 0, 0.57, 0)
MythicalBtn.Size = UDim2.new(0.8, 0, 0, 30)
MythicalBtn.Font = Enum.Font.SourceSansBold
MythicalBtn.Text = "سرقة بيض Mythical 🔮"
MythicalBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
MythicalBtn.TextSize = 13

-- زر سرقة بيض Divine
DivineBtn.Name = "DivineBtn"
DivineBtn.Parent = MainFrame
DivineBtn.BackgroundColor3 = Color3.fromRGB(50, 150, 220)
DivineBtn.Position = UDim2.new(0.1, 0, 0.67, 0)
DivineBtn.Size = UDim2.new(0.8, 0, 0, 30)
DivineBtn.Font = Enum.Font.SourceSansBold
DivineBtn.Text = "سرقة بيض Divine ⚡"
DivineBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
DivineBtn.TextSize = 13

-- زر سرقة بيض Secret
SecretBtn.Name = "SecretBtn"
SecretBtn.Parent = MainFrame
SecretBtn.BackgroundColor3 = Color3.fromRGB(220, 50, 100)
SecretBtn.Position = UDim2.new(0.1, 0, 0.77, 0)
SecretBtn.Size = UDim2.new(0.8, 0, 0, 30)
SecretBtn.Font = Enum.Font.SourceSansBold
SecretBtn.Text = "سرقة بيض Secret 💎"
SecretBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SecretBtn.TextSize = 13

-- زر إعادة التوليد
RespawnButton.Name = "RespawnButton"
RespawnButton.Parent = MainFrame
RespawnButton.BackgroundColor3 = Color3.fromRGB(100, 100, 100)
RespawnButton.Position = UDim2.new(0.1, 0, 0.88, 0)
RespawnButton.Size = UDim2.new(0.8, 0, 0, 25)
RespawnButton.Font = Enum.Font.SourceSansBold
RespawnButton.Text = "إعادة توليد (Respawn)"
RespawnButton.TextColor3 = Color3.fromRGB(255, 255, 255)
RespawnButton.TextSize = 12

-- =========================================
-- منطق الوظائف والأوامر
-- =========================================

local isSpeedActive = false
local speedConnection = nil

local function applySpeed()
    if isSpeedActive and LocalPlayer.Character and LocalPlayer.Character:FindFirstChild("Humanoid") and LocalPlayer.Character:FindFirstChild("HumanoidRootPart") then
        local humanoid = LocalPlayer.Character.Humanoid
        local rootPart = LocalPlayer.Character.HumanoidRootPart
        local desiredSpeed = tonumber(SpeedInput.Text) or 35
        
        humanoid.WalkSpeed = desiredSpeed
        if humanoid.MoveDirection.Magnitude > 0 then
            local currentVelocity = rootPart.AssemblyLinearVelocity
            local moveDir = humanoid.MoveDirection
            rootPart.AssemblyLinearVelocity = Vector3.new(moveDir.X * desiredSpeed, currentVelocity.Y, moveDir.Z * desiredSpeed)
        end
    end
end

ToggleButton.MouseButton1Click:Connect(function()
    isSpeedActive = not isSpeedActive
    if isSpeedActive then
        ToggleButton.Text = "إيقاف السرعة [ON]"
        ToggleButton.BackgroundColor3 = Color3.fromRGB(50, 200, 80)
        if speedConnection then speedConnection:Disconnect() end
        speedConnection = RunService.RenderStepped:Connect(applySpeed)
    else
        ToggleButton.Text = "تشغيل السرعة [OFF]"
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

TeleportButton.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local spawnLocation = workspace:FindFirstChild("SpawnLocation") or workspace:FindFirstChild("Spawn")
        if spawnLocation then
            char.HumanoidRootPart.CFrame = spawnLocation.CFrame + Vector3.new(0, 3, 0)
        else
            char.HumanoidRootPart.CFrame = CFrame.new(0, 10, 0)
        end
    end
end)

local function teleportToEggType(keyword)
    local char = LocalPlayer.Character
    if not char or not char:FindFirstChild("HumanoidRootPart") then return end
    local rootPart = char.HumanoidRootPart
    local targetEgg = nil
    
    for _, obj in ipairs(workspace:GetDescendants()) do
        local nameLower = obj.Name:lower()
        if keyword == "" or nameLower:find(keyword) then
            if (nameLower:find("egg") or nameLower:find("nest")) then
                if obj:IsA("Model") and obj.PrimaryPart then
                    targetEgg = obj.PrimaryPart
                    break
                elseif obj:IsA("BasePart") then
                    targetEgg = obj
                    break
                end
            end
        end
    end
    
    if targetEgg then
        rootPart.CFrame = targetEgg.CFrame + Vector3.new(0, 3, 0)
    else
        rootPart.CFrame = rootPart.CFrame + (rootPart.CFrame.LookVector * 30)
    end
end

AnyEggBtn.MouseButton1Click:Connect(function() teleportToEggType("") end)
MythicalBtn.MouseButton1Click:Connect(function() teleportToEggType("mythical") end)
DivineBtn.MouseButton1Click:Connect(function() teleportToEggType("divine") end)
SecretBtn.MouseButton1Click:Connect(function() teleportToEggType("secret") end)

RespawnButton.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("Humanoid") then
        char.Humanoid.Health = 0
    end
end)
