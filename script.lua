-- Steal An Egg - Areas Teleport Hub 
local Players = game:GetService("Players")
local LocalPlayer = Players.LocalPlayer
local PlayerGui = LocalPlayer:WaitForChild("PlayerGui")

if PlayerGui:FindFirstChild("EggHubGui") then
    PlayerGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
ScreenGui.Parent = PlayerGui
ScreenGui.ResetOnSpawn = false

-- النافذة الرئيسية
local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.3, 0, 0.2, 0)
MainFrame.Size = UDim2.new(0, 260, 0, 340)
MainFrame.Active = true
MainFrame.Draggable = true

-- عنوان القائمة
local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Teleport Areas Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- زر منطقة الأمان / البداية (Spawn)
local SpawnBtn = Instance.new("TextButton")
SpawnBtn.Parent = MainFrame
SpawnBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SpawnBtn.Position = UDim2.new(0.1, 0, 0.18, 0)
SpawnBtn.Size = UDim2.new(0.8, 0, 0, 40)
SpawnBtn.Text = "منطقة البداية / الأمان 🛡️"
SpawnBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SpawnBtn.TextSize = 14
SpawnBtn.Font = Enum.Font.SourceSansBold

-- زر الانتقال للمنطقة الأولى (Area 1)
local Area1Btn = Instance.new("TextButton")
Area1Btn.Parent = MainFrame
Area1Btn.BackgroundColor3 = Color3.fromRGB(80, 80, 100)
Area1Btn.Position = UDim2.new(0.1, 0, 0.35, 0)
Area1Btn.Size = UDim2.new(0.8, 0, 0, 40)
Area1Btn.Text = "الانتقال للمنطقة الأولى 📍"
Area1Btn.TextColor3 = Color3.fromRGB(255, 255, 255)
Area1Btn.TextSize = 14
Area1Btn.Font = Enum.Font.SourceSansBold

-- زر الانتقال للمنطقة الثانية (Area 2)
local Area2Btn = Instance.new("TextButton")
Area2Btn.Parent = MainFrame
Area2Btn.BackgroundColor3 = Color3.fromRGB(150, 50, 200)
Area2Btn.Position = UDim2.new(0.1, 0, 0.52, 0)
Area2Btn.Size = UDim2.new(0.8, 0, 0, 40)
Area2Btn.Text = "الانتقال للمنطقة الثانية ⚡"
Area2Btn.TextColor3 = Color3.fromRGB(255, 255, 255)
Area2Btn.TextSize = 14
Area2Btn.Font = Enum.Font.SourceSansBold

-- زر الانتقال للمنطقة المتقدمة / الأخيرة (Area 3)
local Area3Btn = Instance.new("TextButton")
Area3Btn.Parent = MainFrame
Area3Btn.BackgroundColor3 = Color3.fromRGB(220, 100, 30)
Area3Btn.Position = UDim2.new(0.1, 0, 0.69, 0)
Area3Btn.Size = UDim2.new(0.8, 0, 0, 40)
Area3Btn.Text = "الانتقال للمنطقة المتقدمة 💎"
Area3Btn.TextColor3 = Color3.fromRGB(255, 255, 255)
Area3Btn.TextSize = 14
Area3Btn.Font = Enum.Font.SourceSansBold

-- زر إعادة التوليد
local RespawnBtn = Instance.new("TextButton")
RespawnBtn.Parent = MainFrame
RespawnBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
RespawnBtn.Position = UDim2.new(0.1, 0, 0.86, 0)
RespawnBtn.Size = UDim2.new(0.8, 0, 0, 32)
RespawnBtn.Text = "إعادة توليد (Respawn) 🔄"
RespawnBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
RespawnBtn.TextSize = 13
RespawnBtn.Font = Enum.Font.SourceSansBold

-- ==========================================
-- منطق الانتقال للمناطق
-- ==========================================

-- دالة عامة للبحث عن أجزاء المنطقة أو البوابات والانتقال لها
local function teleportToArea(keyword)
    local char = LocalPlayer.Character
    if not char or not char:FindFirstChild("HumanoidRootPart") then return end
    local root = char.HumanoidRootPart
    
    local targetPart = nil
    for _, obj in ipairs(workspace:GetDescendants()) do
        local nameLower = obj.Name:lower()
        if nameLower:find(keyword) then
            if obj:IsA("Model") and obj.PrimaryPart then
                targetPart = obj.PrimaryPart
                break
            elseif obj:IsA("BasePart") then
                targetPart = obj
                break
            end
        end
    end
    
    if targetPart then
        root.CFrame = targetPart.CFrame + Vector3.new(0, 3, 0)
    else
        -- إذا لم يجد جزءاً بالاسم، يتحرك للأمام مسافة معينة بحسب المنطقة
        root.CFrame = root.CFrame + (root.CFrame.LookVector * 100)
    end
end

-- زر منطقة البداية (Spawn)
SpawnBtn.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local spawn = workspace:FindFirstChild("SpawnLocation") or workspace:FindFirstChild("Spawn")
        if spawn then
            char.HumanoidRootPart.CFrame = spawn.CFrame + Vector3.new(0, 3, 0)
        else
            char.HumanoidRootPart.CFrame = CFrame.new(0, 10, 0)
        end
    end
end)

-- أزرار مناطق الماب المختلفة
Area1Btn.MouseButton1Click:Connect(function()
    teleportToArea("area1") or teleportToArea("zone1") or teleportToArea("island1")
end)

Area2Btn.MouseButton1Click:Connect(function()
    teleportToArea("area2") or teleportToArea("zone2") or teleportToArea("island2")
end)

Area3Btn.MouseButton1Click:Connect(function()
    teleportToArea("area3") or teleportToArea("zone3") or teleportToArea("island3")
end)

RespawnBtn.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("Humanoid") then
        char.Humanoid.Health = 0
    end
end)
