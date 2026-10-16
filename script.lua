-- Steal An Egg - Auto Steal & Target Menu Hub
local Players = game:GetService("Players")
local LocalPlayer = Players.LocalPlayer
local PlayerGui = LocalPlayer:WaitForChild("PlayerGui")
local RunService = game:GetService("RunService")

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
MainFrame.Size = UDim2.new(0, 260, 0, 320)
MainFrame.Active = true
MainFrame.Draggable = true

-- عنوان القائمة
local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Steal An Egg - Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- مربع اختيار الحيوان/البيضة المستهدفة (Target Egg)
local TargetLabel = Instance.new("TextLabel")
TargetLabel.Parent = MainFrame
TargetLabel.BackgroundTransparency = 1
TargetLabel.Position = UDim2.new(0.1, 0, 0.15, 0)
TargetLabel.Size = UDim2.new(0.8, 0, 0, 20)
TargetLabel.Text = "اختر نوع البيضة / الحيوان المستهدف:"
TargetLabel.TextColor3 = Color3.fromRGB(180, 180, 180)
TargetLabel.TextSize = 13
TargetLabel.Font = Enum.Font.SourceSans

local EggDropdown = Instance.new("TextBox")
EggDropdown.Parent = MainFrame
EggDropdown.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
EggDropdown.Position = UDim2.new(0.1, 0, 0.23, 0)
EggDropdown.Size = UDim2.new(0.8, 0, 0, 35)
EggDropdown.Text = "Secret" -- اكتب هنا اسم الحيوان أو الرتبة (مثل Secret أو Divine أو Nightflame)
EggDropdown.TextColor3 = Color3.fromRGB(0, 255, 150)
EggDropdown.TextSize = 15
EggDropdown.Font = Enum.Font.SourceSansBold

-- زر تحديث البيض (Refresh Eggs)
local RefreshBtn = Instance.new("TextButton")
RefreshBtn.Parent = MainFrame
RefreshBtn.BackgroundColor3 = Color3.fromRGB(45, 45, 60)
RefreshBtn.Position = UDim2.new(0.1, 0, 0.42, 0)
RefreshBtn.Size = UDim2.new(0.8, 0, 0, 35)
RefreshBtn.Text = "Refresh Eggs 🔄"
RefreshBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
RefreshBtn.TextSize = 14
RefreshBtn.Font = Enum.Font.SourceSansBold

-- زر السرقة التلقائية (Auto Steal Toggle)
local AutoStealBtn = Instance.new("TextButton")
AutoStealBtn.Parent = MainFrame
AutoStealBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
AutoStealBtn.Position = UDim2.new(0.1, 0, 0.60, 0)
AutoStealBtn.Size = UDim2.new(0.8, 0, 0, 45)
AutoStealBtn.Text = "Auto Steal: [OFF]"
AutoStealBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
AutoStealBtn.TextSize = 16
AutoStealBtn.Font = Enum.Font.SourceSansBold

-- زر العودة لمنطقة الأمان
local SafeZoneBtn = Instance.new("TextButton")
SafeZoneBtn.Parent = MainFrame
SafeZoneBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SafeZoneBtn.Position = UDim2.new(0.1, 0, 0.81, 0)
SafeZoneBtn.Size = UDim2.new(0.8, 0, 0, 38)
SafeZoneBtn.Text = "العودة لمنطقة الأمان 🛡️"
SafeZoneBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SafeZoneBtn.TextSize = 14
SafeZoneBtn.Font = Enum.Font.SourceSansBold

-- ==========================================
-- منطق البرمجة للسرقة التلقائية
-- ==========================================

local autoStealActive = false
local stealConnection = nil

AutoStealBtn.MouseButton1Click:Connect(function()
    autoStealActive = not autoStealActive
    
    if autoStealActive then
        AutoStealBtn.Text = "Auto Steal: [ON]"
        AutoStealBtn.BackgroundColor3 = Color3.fromRGB(50, 200, 80)
        
        -- حلقة بحث وسرقة تلقائية للبيضة المحددة
        stealConnection = task.spawn(function()
            while autoStealActive do
                local char = LocalPlayer.Character
                if char and char:FindFirstChild("HumanoidRootPart") then
                    local targetName = EggDropdown.Text:lower()
                    local foundTarget = nil
                    
                    -- البحث في الخريطة عن البيضة التي تطابق الاختيار
                    for _, obj in ipairs(workspace:GetDescendants()) do
                        local objName = obj.Name:lower()
                        if objName:find(targetName) or objName:find("egg") or objName:find("nest") then
                            if obj:IsA("Model") and obj.PrimaryPart then
                                foundTarget = obj.PrimaryPart
                                break
                            elseif obj:IsA("BasePart") then
                                foundTarget = obj
                                break
                            end
                        end
                    end
                    
                    -- الانتقال للبيضة وسرقتها تلقائياً
                    if foundTarget then
                        char.HumanoidRootPart.CFrame = foundTarget.CFrame + Vector3.new(0, 3, 0)
                    end
                end
                task.wait(1) -- فحص كل ثانية
            end
        end)
    else
        AutoStealBtn.Text = "Auto Steal: [OFF]"
        AutoStealBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
        autoStealActive = false
    end
end)

-- زر التحديث
RefreshBtn.MouseButton1Click:Connect(function()
    RefreshBtn.Text = "Refreshed! ✅"
    task.wait(1)
    RefreshBtn.Text = "Refresh Eggs 🔄"
end)

-- زر الأمان
SafeZoneBtn.MouseButton1Click:Connect(function()
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
